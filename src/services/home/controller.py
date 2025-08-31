from fastapi import Request, HTTPException
from src.lib.db import db_session
from src.lib.session import SessionDataService
from src.services.home.serializer import ConsentInBound
from src.lib.session import SessionDataService as session
from src.configs.constants import RedisKeys
from fastapi.responses import RedirectResponse


class HomeController:
    @staticmethod
    async def is_k1_recipient(company_id: int, contact_id: int):
        objK1Recipient = db_session.execute_query(
            "select dbo.fn_IsK1Recipient(:CompanyID, :ContactID) AS IsK1Recipient",
            params={
                "CompanyID": company_id,
                "ContactID": contact_id
            }
        )

        return bool(objK1Recipient[0].get("IsK1Recipient", False)) if len(objK1Recipient) > 0 else False
    
    @staticmethod
    def has_lp_k1_consent(company_id: int):
        result = db_session.call_procedure(
            "pr_PartnerK1Consent",
            params={
                "CompanyID": company_id
            }
        )
        
        return len(result) > 0
    
    @staticmethod
    def is_consenter(company_id: int, contact_id: int):
        objConsenterRS = db_session.call_procedure(
            "pr_PartnerK1Consenter",
            params={
                "CompanyID": company_id,
                "ContactID": contact_id,
            }
        )
        
        return len(objConsenterRS) > 0
    
    @staticmethod
    def show_k1_consent_agreement(company_id: int, contact_id: int, is_k1_recepient: bool):
        showConsent = True

        if HomeController.has_lp_k1_consent(company_id):
            showConsent = False

        if HomeController.is_consenter(company_id, contact_id) == False and is_k1_recepient == False:
            showConsent = False

        return showConsent
    
    @staticmethod
    def get_consent_view_model(company_id: int, contact_id: int):
        return {
            "objConsenterListRS": db_session.call_procedure("pr_PartnerK1ConsenterList", params={
                "CompanyID": company_id
            }),
            "objConsentersCompanyListRS": db_session.call_procedure("pr_PartnerK1ConsentersCompanyList", params={
                "ContactID": contact_id
            }),
            "objConsenterRS": db_session.call_procedure("pr_PartnerK1Consenter", params={
                "CompanyID": company_id,
                "ContactID": contact_id
            }),
            "IsConsenter": HomeController.is_consenter(company_id, contact_id)
        }

    @staticmethod
    async def index(request: Request):
        bit_show_popup, bit_has_lp, count = False, False, 0
        
        curr_user_id = await session.get_session_data(request, RedisKeys.CURRENT_USER_ID)
        curr_user_id = int(curr_user_id) if curr_user_id else 0
        curr_user_lp_id = await session.get_session_data(request, RedisKeys.CURRENT_USER_LP_ID)
        curr_user_lp_id = int(curr_user_lp_id) if curr_user_lp_id else 0
        
        print(curr_user_id, curr_user_lp_id)
        
        if not curr_user_id:
            await session.set_session_data(request, RedisKeys.PERMISSION_MYSEQUOIA_CAPITAL, False)
            return RedirectResponse(url="/errordisplay")

        if curr_user_lp_id:
            bit_has_lp = True
            
        objRS = db_session.call_procedure(
            "pr_PartnerRecentActivity",
            params={
                "ContactID": curr_user_id, 
                "CompanyID": curr_user_lp_id or 0
                }
        )

        objReminderRS = db_session.call_procedure(
            "pr_PartnerReminders",
            params={
                "ContactID": curr_user_id, 
                "CompanyID": curr_user_lp_id or 0
                }
        )

        objFStmtRS = db_session.call_procedure(
            "pr_PartnerMailingRecentByEventDate",
            params={
                "ContactID": curr_user_id, 
                "CompanyID": curr_user_lp_id or 0,
                "MailingTypeID": 1
                }
        )

        objK1RS = db_session.call_procedure(
            "pr_PartnerK1FileListMostRecent",
            params={
                "ContactID": curr_user_id, 
                "LPID": curr_user_lp_id or 0
                }
        )

        objSCGEK1RS = db_session.call_procedure(
            "pr_PartnerSCGEK1FileListMostRecent",
            params={
                "ContactID": curr_user_id, 
                "LPID": curr_user_lp_id or 0
                }
        )
        
        unique_files = dict()
        for row in objK1RS:
            result = db_session.call_procedure(
                "pr_PartnerMailingFileList",
                params={
                    "MID": row.get("MailingID"),
                    "CompanyID": curr_user_lp_id or 0,
                    "ContactID": curr_user_id,
                    
                }
            )
            if len(result) > 0:
                fileRow = result[0]
                key = str(fileRow.get("MailingID"))
                if key not in unique_files:
                    unique_files[key] = fileRow
                    
        boolK1Recipient: bool = await HomeController.is_k1_recipient(
            curr_user_lp_id or 0,
            curr_user_id
        )
        
        objConsenterRS = db_session.call_procedure(
            "pr_PartnerK1Consenter",
            params={
                "ContactID": curr_user_id, 
                "CompanyID": curr_user_lp_id or 0,
            }
        )
        
        is_consenter = len(objConsenterRS) > 0
        
        from datetime import datetime, timedelta

        bit_display_fstmt = False

        # Assuming objFStmtRS is a SQLAlchemy result from execute or execute_query
        for row in objFStmtRS:
            mailing_date = row["MailingDate"]
            print("Mailing_date", mailing_date)
            if isinstance(mailing_date, str):
                mailing_date = datetime.fromisoformat(mailing_date)  # convert string to datetime if needed
            if (datetime.now() - mailing_date).days <= 30:
                bit_display_fstmt = True
                break
            
        hasLPK1Consent = len(db_session.call_procedure(
                    "pr_PartnerK1Consent",
                    params={
                        "CompanyID": curr_user_lp_id or 0,
                    }
                )) > 0
        
        showK1ConsentAgreement = HomeController.show_k1_consent_agreement(
            curr_user_lp_id,
            curr_user_id,
            boolK1Recipient
        )
        
        return {
            "currUserID": curr_user_id,    
            "currUserLPID": curr_user_lp_id or 0,
            "objRS": objRS,
            "objReminderRS": objReminderRS,
            "objFStmtRS": objFStmtRS,
            "objK1RS": objK1RS,
            "objSCGEK1RS": objSCGEK1RS,
            "objFileRS": unique_files,
            "boolK1Recipient": boolK1Recipient,
            "HasLPK1Consent": False and hasLPK1Consent,
            "IsConsenter": is_consenter,
            "ShowK1ConsentAgreement": showK1ConsentAgreement,
            "bitDisplayFStmt": True or bit_display_fstmt,
            # ! "strBlackBarText": strBlackBarText, -- not sure why its passed
            # ! "bitShowPopup": bitShowPopup, -- not sure why its passed
            "bitHasLP": bit_has_lp,
            "consentViewModel": HomeController.get_consent_view_model(company_id=curr_user_lp_id, contact_id=curr_user_id)
        }
        

    @staticmethod
    async def process_k1_consent(request: Request, payload: ConsentInBound):
        try:
            consentersCompanyList = db_session.call_procedure(
                "pr_PartnerK1ConsentersCompanyList",
                params={
                    "ContactID": payload.ContactID
                }
            );

            for row in consentersCompanyList:
                consentParameters = { "CompanyID": payload.CompanyID ,
                    "ContactID": payload.ContactID ,
                    "RoleID": payload.RoleID ,
                    "IP": request.headers.ip
                }

                db_session.call_procedure(
                    "pr_PartnerK1ConsentUpdate",
                    consentParameters
                )
            
            return {
                "success": True
            }
        except Exception as e:
            return HTTPException(status_code=400, content={ "error": "Something went wrong"})
            
