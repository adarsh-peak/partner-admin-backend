from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional, List
from src.configs.constants import RedisKeys
from src.lib.session import SessionDataService as session
from src.lib.db import db_session
from src.utils.common import parse_date_string, safe_int
from datetime import datetime

class FinancialStatementController:
    @staticmethod
    def get_partner_recent_by_event_date(contact_id: int, company_id: int, mailing_type_id: int, excludeSCFFunds: bool, event_date: datetime, strict_date: bool):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
            "ExcludeSCFFunds": excludeSCFFunds,
        }
        
        if event_date:
            params["EventDate"] = event_date
            params["StrictDate"] = strict_date
            
        return db_session.call_procedure("pr_PartnerMailingRecentByEventDate", params)
    
    @staticmethod
    def get_recent_partner_mailing_by_event_date_with_fallback(contact_id: int, company_id: int, mailing_type_id: int, excludeSCFFunds: bool, event_date: datetime, strict_date: bool, objMenuRS: List[object]):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
            "ExcludeSCFFunds": excludeSCFFunds,
        }
        
        if event_date:
            params["EventDate"] = event_date
            params["StrictDate"] = strict_date
        elif len(objMenuRS):
            raw_event_date = objMenuRS[0].get("EventDate", None)
            params["StrictDate"] = True
            params["EventDate"] = raw_event_date
            
        return db_session.call_procedure("pr_PartnerMailingRecentByEventDate", params)
    
    @staticmethod
    def get_partner_mailing_quaterly_by_event_date_and_multiple_mailing_types(contact_id: int, company_id: int, mailing_type_id_1: int, mailing_type_id_2: int, event_date: str):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID1": mailing_type_id_1,
            "MailingTypeID2": mailing_type_id_2,
            "EventDate": event_date,
        }
        
        return db_session.call_procedure("pr_PartnerMailingQuartersByEventDateAndMultipleMailingTypes", params)
    
    @staticmethod
    def get_partner_mailing_years_by_event_date_and_multiple_mailing_types(contact_id: int, company_id: int, mailing_type_id_1: int, mailing_type_id_2: int, event_date: str):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID1": mailing_type_id_1,
            "MailingTypeID2": mailing_type_id_2,
            "EventDate": event_date,
        }
        
        return db_session.call_procedure("pr_PartnerMailingYearsByEventDateAndMultipleMailingTypes", params)
    
    @staticmethod
    def get_partner_FStmt_summary(contact_id: int, company_id: int, event_date: str):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "EventDate": event_date,
        }
        
        return db_session.call_procedure("pr_PartnerFStmtSummary", params)
    
    @staticmethod
    def get_partner_FStmt_summary_grand_totals(contact_id: int, company_id: int):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
        }
        
        return db_session.call_procedure("pr_PartnerFStmtSummaryGrandTotals", params)
    
    @staticmethod
    def get_lp_info(contact_id: int, company_id: int):
        params = {
            "CompanyID": company_id,
            "ContactID": contact_id,
        }
        
        return db_session.call_procedure("pr_PartnerMySequoiaLPInfo", params)
    
    @staticmethod
    def get_company_name(company_id: int):
        params = {
            "CompanyID": company_id,
        }
        
        return db_session.call_procedure("pr_AdminCompanyName", params)
    
    @staticmethod
    def get_partner_mailing_info(contact_id: int, company_id: int, mailing_id: int):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingID": mailing_id,
        }
        
        return db_session.call_procedure("pr_PartnerMailingInfo", params)
    
    @staticmethod
    def get_partner_most_recent_mailing(contact_id: int, company_id: int, mailing_type_id: int):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
        }
        
        return db_session.call_procedure("pr_PartnerMostRecentMailing", params)
    
    @staticmethod
    async def prepare_financial_statement_view_model(request: Request, mid: str, date: str):
        mailing_id, selected_date = safe_int(mid), parse_date_string(date)

        curr_user_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_ID
        )
        curr_user_id = safe_int(curr_user_id, 0)
        curr_user_lp_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_LP_ID
        )
        curr_user_lp_id = safe_int(curr_user_lp_id, 0)
        
        if not curr_user_id or not curr_user_lp_id:
            return None
        
        objMenuRS = FinancialStatementController.get_partner_recent_by_event_date(curr_user_id, curr_user_lp_id, 1, True, selected_date, bool(selected_date))
        
        event_date = None
        if len(objMenuRS):
            event_date = objMenuRS[0].get("EventDate", None)
            mailing_id = mailing_id if mailing_id else objMenuRS[0].get("MailingID", None)
            
        objMenuMCRS = FinancialStatementController.get_recent_partner_mailing_by_event_date_with_fallback(curr_user_id, curr_user_lp_id, 20, True, selected_date, bool(selected_date), objMenuRS)
        
        if len(objMenuMCRS):
            if not event_date:
                event_date = objMenuMCRS[0].get("EventDate", None)
            if not mailing_id:
                mailing_id = safe_int(objMenuMCRS[0].get("MailingID", None))
        
        objMenuFStmtQuartersRS, objMenuYearsRS = None, None
        
        if len(objMenuRS) > 0 or len(objMenuMCRS) > 0:
            objMenuFStmtQuartersRS = FinancialStatementController.get_partner_mailing_quaterly_by_event_date_and_multiple_mailing_types(curr_user_id, curr_user_lp_id, 1, 20, event_date)
            
            objMenuYearsRS = FinancialStatementController.get_partner_mailing_years_by_event_date_and_multiple_mailing_types(curr_user_id, curr_user_lp_id, 1, 20, event_date)
            
            if "/financial_statement" in request.base_url.path and not mailing_id:
                if len(objMenuRS) > 0:
                    mailing_id = safe_int(objMenuRS[0].get("MailingID", None))
                    
                if len(objMenuMCRS) > 0 and not mailing_id:
                    mailing_id = safe_int(objMenuMCRS[0].get("MailingID", None))
        
        objSummaryFStmtRS = FinancialStatementController.get_partner_FStmt_summary(curr_user_id, curr_user_lp_id, selected_date)
            
        objSummaryTotalsRS = FinancialStatementController.get_partner_FStmt_summary_grand_totals(curr_user_id, curr_user_lp_id)
        
        objLPInfoRS = FinancialStatementController.get_lp_info(curr_user_id, curr_user_lp_id)
        objCompanyNameRS = FinancialStatementController.get_company_name(curr_user_lp_id)
        objPartnerMailingInfo = FinancialStatementController.get_partner_mailing_info(curr_user_id, curr_user_lp_id, mailing_id)
        objPartnerMostRecentMailing = FinancialStatementController.get_partner_most_recent_mailing(curr_user_id, curr_user_lp_id, 1)
        
        return {
            "MailingID": mailing_id,
            "EventDate": selected_date,
            "MenuRS": objMenuRS,
            "MenuMCRS": objMenuMCRS,
            "MenuFStmtQuartersRS": objMenuFStmtQuartersRS,
            "MenuYearsRS": objMenuYearsRS,
            "SummaryFStmtRS": objSummaryFStmtRS,
            "SummaryTotalsRS": objSummaryTotalsRS,
            "LPInfoRS": objLPInfoRS,
            "objCompanyNameRS": objCompanyNameRS,
            "PartnerMailingInfoRS": objPartnerMailingInfo,
            "PartnerMostRecentMailing": objPartnerMostRecentMailing,

            "ShowFStmt": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMT) or False,
            "ShowFStmtMC": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMTMC) or False,
            "ShowSAnnual": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_SANNUAL) or False,
            "ShowAudFS": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_AUD_FS) or False,
        }
        

    @staticmethod
    async def get_quaterly_report(request: Request, mid: Optional[str] = None, date: Optional[str] = None
    ):
        view_model = await (
            FinancialStatementController.prepare_financial_statement_view_model(
                request, mid, date
            )
        )

        if not view_model:
            return RedirectResponse(url="/")

        return {"data": view_model}
    
    @staticmethod
    def get_partner_mailing_recent_by_event_date_with_files(contact_id: int, company_id: int, mailing_type_id: int, eventDate: datetime):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
        }
        
        if eventDate:
            params["EventDate"] = eventDate
            
        return db_session.call_procedure("pr_PartnerMailingRecentByEventDateWithFiles", params)
    
    @staticmethod
    def get_partner_mailing_recent_semi_annual_geo_with_files(contact_id: int, company_id: int, eventDate: datetime):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
        }
        
        if eventDate:
            params["EventDate"] = eventDate
            
        return db_session.call_procedure("pr_PartnerMailingRecentSAnnualGeoWithFiles", params)
    
    @staticmethod
    def get_partner_mailing_quaters_by_event_date(contact_id: int, company_id: int, mailing_type_id: int, eventDate: datetime):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
            "EventDate": eventDate
        }
            
        return db_session.call_procedure("pr_PartnerMailingQuartersByEventDate", params)
    
    @staticmethod
    def get_partner_mailing_years_by_event_date(contact_id: int, company_id: int, mailing_type_id: int, eventDate: datetime):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
            "EventDate": eventDate
        }
            
        return db_session.call_procedure("pr_PartnerMailingYearsByEventDate", params)
    
    @staticmethod
    async def prepare_menu_semi_annuak_view_model(request: Request, mid: Optional[str] = None, date: Optional[str] = None):
        curr_user_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_ID
        )
        curr_user_id = safe_int(curr_user_id, 0)
        curr_user_lp_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_LP_ID
        )
        curr_user_lp_id = safe_int(curr_user_lp_id, 0)
        
        mailing = ""
        if mid:
            mailing = mid
            
        objMenuRS = FinancialStatementController.get_partner_mailing_recent_by_event_date_with_files(curr_user_id, curr_user_lp_id, 8, parse_date_string(date))
        
        objMenuGeoRS = FinancialStatementController.get_partner_mailing_recent_semi_annual_geo_with_files(curr_user_id, curr_user_lp_id, parse_date_string(date))
        
        date_event, showSA = None, False
        if len(objMenuRS) > 0:
            date_event = parse_date_string(objMenuRS[0].get("EventDate"))
            mailing = objMenuRS[0].get("MailingID")
            showSA = True
            
            if len(objMenuGeoRS) > 0:
                if parse_date_string(objMenuGeoRS[0].get("EventDate")) > parse_date_string(objMenuRS[0].get("EventDate")):
                    date_event = parse_date_string(objMenuGeoRS[0].get("EventDate"))
                    showSA = False
                    mailing = objMenuGeoRS[0].get("MailingID")
            else:
                if len(objMenuGeoRS) > 0:
                    date_event = parse_date_string(objMenuGeoRS[0].get("EventDate"))
                    mailing = objMenuGeoRS[0].get("MailingID")
                    
        objLPInfoRS = FinancialStatementController.get_lp_info(curr_user_id, curr_user_lp_id)
        showMenuTimeframe = False
        
        if not date_event and not bool(objLPInfoRS.Rows[0]["IsRestrictedAccess"]):
            showMenuTimeframe = True
        
        objMenuQuartersRS, objMenuYearsRS = None, None
        if showMenuTimeframe:
            objMenuQuartersRS = FinancialStatementController.get_partner_mailing_quaters_by_event_date(curr_user_id, curr_user_lp_id, 8, date_event)
            objMenuYearsRS = FinancialStatementController.get_partner_mailing_years_by_event_date(
                curr_user_id, curr_user_lp_id, 8, date_event
            )
            
        return {
            "MenuRS": objMenuRS,
            "ShowSA": showSA,
            "DateEvent": date_event,
            "intMailing": mailing,
            "ShowMenuTimeframe": showMenuTimeframe,
            "MenuQuartersRS": objMenuQuartersRS,
            "MenuYearsRS": objMenuYearsRS,
            "ShowFStmt": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMT) or False,
            "ShowFStmtMC": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMTMC) or False,
            "ShowSAnnual": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_SANNUAL) or False,
            "ShowAudFS": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_AUD_FS) or False,
        }
        
    @staticmethod
    def get_mailing_subject(mailing_id:int, company_id: int):
        query = """
            SELECT M.Subject
            FROM Mailing M
            WHERE M.MailingID = @MailingID
            AND NOT EXISTS (
                SELECT *
                FROM MailingExceptionExclude
                WHERE LP_CompanyID = @CompanyID
                AND FundID = M.FundID
                AND MailingTypeID = M.MailingTypeID
        """
        params = {
            "MailingID": mailing_id,
            "CompanyID": company_id,
        }
        
        
        return db_session.execute_query(query, params)
        
    
    @staticmethod
    async def prepare_summary_semi_annual_view_model(request: Request, mid: Optional[str] = None, date: Optional[str] = None, menuViewModel: Optional = None):
        curr_user_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_ID
        )
        curr_user_id = safe_int(curr_user_id, 0)
        curr_user_lp_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_LP_ID
        )
        curr_user_lp_id = safe_int(curr_user_lp_id, 0)
        
        objLPInfoRS = FinancialStatementController.get_lp_info(curr_user_id, curr_user_lp_id)
        mailing_RA = None
        mailing = None
        
        if len(objLPInfoRS) > 0 and bool(objLPInfoRS[0]["IsRestrictedAccess"]):
            mailing_RA = {
                "objSAGeoRARS": FinancialStatementController.get_partner_mailing_recent_semi_annual_geo_with_files(curr_user_id, curr_user_lp_id, null)
            }
        else:
            mailing = None
            if mid:
                mailing = mid
                
            objRS = FinancialStatementController.get_partner_mailing_info(curr_user_id, curr_user_lp_id, safe_int(mailing))
            
            if len(objRS) > 0:
                objRS = FinancialStatementController.get_mailing_subject(safe_int(mailing), curr_user_lp_id)
            
            objSAGeoRS = None
            if not mid:
                objSAGeoRS = FinancialStatementController.get_partner_mailing_recent_semi_annual_geo_with_files(curr_user_id, curr_user_lp_id, menuViewModel.get("DateEvent"))
                
            mailing = {
                "objRS":objRS,
                "DateEvent":menuViewModel.get("DateEvent"),
                "MenuRS":menuViewModel.get("MenuRS"),
                "objSAGeoRS":objSAGeoRS,
                "ShowSA":menuViewModel.get("ShowSA"),
                "intMailing":mailing,
            }
            
        return {
            "LPInfoRS": objLPInfoRS,
            "mailing_RA": mailing_RA,
            "mailing": mailing
        }
    
    @staticmethod
    async def get_semi_annual_reports(request: Request, mid: Optional[str] = None, date: Optional[str] = None):
        menuViewModel = await FinancialStatementController.prepare_menu_semi_annuak_view_model(request, mid, date)
        summaryViewModel = await FinancialStatementController.prepare_summary_semi_annual_view_model(request, mid, date, menuViewModel)
        return {
            "menuViewModel": menuViewModel,
            "summaryViewModel": summaryViewModel,
        }
        
    @staticmethod
    def get_partner_mailing_recent_by_event_date_audited_fstmt(contact_id: int, company_id: int, mailing_type_id: int, event_date: datetime):
        params = {
            "ContactID": contact_id,
            "CompanyID": company_id,
            "MailingTypeID": mailing_type_id,
        }
        
        if event_date:
            params["EventDate"] = event_date
            
        return db_session.call_procedure("pr_PartnerMailingRecentByEventDate", params)
        
    @staticmethod
    async def prepare_audited_financial_statement_view_model(request: Request, mid: Optional[str] = None, date: Optional[str] = None):
        mailing_id = safe_int(mid)
        selected_date = parse_date_string(date)
        
        curr_user_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_ID
        )
        curr_user_id = safe_int(curr_user_id, 0)
        curr_user_lp_id = await session.get_session_data(
            request, RedisKeys.CURRENT_USER_LP_ID
        )
        curr_user_lp_id = safe_int(curr_user_lp_id, 0)
        
        if not curr_user_id or not curr_user_lp_id:
            raise HTTPException(
            status_code=401,
            detail="Unauthorised User",
        )
        
        objMenuRS = FinancialStatementController.get_partner_mailing_recent_by_event_date_audited_fstmt(curr_user_id, curr_user_lp_id, 9, selected_date)
        
        objMenuYearsRS = None
        # ! Not sure why this block exists
        # DataTable objMenuYearsRS = null;
        # if (objMenuRS.Rows.Count > 0)
        # {
        #     var eventDate =
        #         objMenuRS.Rows[0]["EventDate"] != DBNull.Value
        #             ? (DateTime?)objMenuRS.Rows[0]["EventDate"]
        #             : DateTime.Now;
        #     objMenuYearsRS = financialStatementsService.GetPartnerMailingYearsByEventDate(
        #         int.Parse(userId),
        #         int.Parse(userLpid),
        #         9, // MailingTypeID
        #         eventDate.GetValueOrDefault(DateTime.Now)
        #     );
        # }
        
        objLPInfoRS = FinancialStatementController.get_lp_info(curr_user_id, curr_user_lp_id)
        
        return {
            "MailingId": mailing_id,
            "MenuRS": objMenuRS,
            "MenuYearsRS": objMenuYearsRS,
            "LPInfoRS": objLPInfoRS,
            "SelectedDate": selected_date,
            "ShowFStmt": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMT) or False,
            "ShowFStmtMC": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_FSTMTMC) or False,
            "ShowSAnnual": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_SANNUAL) or False,
            "ShowAudFS": await session.get_session_data(request, RedisKeys.MY_SC_VIEW_AUD_FS) or False,
        }
        

    @staticmethod
    async def get_annual_report(request: Request, mid: Optional[str] = None, date: Optional[str] = None):
        viewModel = await FinancialStatementController.prepare_audited_financial_statement_view_model(request, mid, date)
        
        if not viewModel:
            return RedirectResponse(url='/dashboard')
        
        return viewModel