from fastapi import Depends, HTTPException, Request
from src.lib.session import SessionDataService as session
from src.configs.constants import RedisKeys

class AuthorisationService:

  async def authorize_user(request: Request) -> bool:
    
    objSiteAccessListRS: dict = {}
    boolIsNewSession: bool = False
    identityToImpersonate: str = ""
    strSiteName: str = "partnerlogin"
    strBlackBarText: str = ""

    curr_user_id = await session.get_session_data(request, RedisKeys.CURRENT_USER_ID)
    curr_user_id = int(curr_user_id) if curr_user_id else 0
    curr_user_lp_id = await session.get_session_data(request, RedisKeys.CURRENT_USER_LP_ID)
    curr_user_lp_id = int(curr_user_lp_id) if curr_user_lp_id else 0
    
    if curr_user_id:
      boolIsNewSession = True
    
    # ! Set true identity prior to impersonation
    # SessionDataService.SetSessionData(
    #     "TrueUserID",
    #     userService.GetContactIDFromCredentials()
    # );
    
    # ! Check site access for the true user
    # if (
    #     !userService.GetLoginSiteAccessSelect(
    #         SessionDataService.GetSessionData("TrueUserID")
    #     )
    # )
    # {
    #     throw new Exception("User is not authorized on this site.");
    # }
    
    # ! Pending on user service
    # identityToImpersonate = userService.GetIdentityToImpersonate();

    # if identity_to_impersonate and identity_to_impersonate.isdigit():
    #     # Call stored procedure to get region info
    #     obj_region_rs = db_session.call_procedure(
    #         "pr_AdminContactRegionSelect",
    #         params={"ContactID": identity_to_impersonate}
    #     )

    #     # Set CurrUserID to TrueUserID initially
    #     session["CurrUserID"] = session.get("TrueUserID")

    #     region = obj_region_rs[0]["Region"]  # assuming call_procedure returns list of dicts
    #     if user_service.contact_has_node_access("ContactLoginPartnerLoginLoginLink", region):
    #         # Impersonation allowed
    #         session["CurrUserID"] = identity_to_impersonate
    #     else:
    #         true_user = session.get("TrueUserID")
    #         raise HTTPException(
    #             status_code=403,
    #             detail=f"User {true_user} is not authorized to impersonate."
    # )
    
    # if curr_user_id:
    #   await session.set_session_data(request, RedisKeys.CURRENT_USER_ID, await session.get_session_data(request, RedisKeys.TRUE_USER_ID))
      
    # ! Get site specific login credentials and set session
    # objSiteAccessListRS = userService
    #             .GetLoginSiteAccessList(SessionDataService.GetSessionData("CurrUserID"))
    #             .Result;
    #         userService.SetLoginSession(objSiteAccessListRS);
  
    # ! Log site access
    # if (boolIsNewSession && !userService.IsUserImpersonating())
    # {
    #     userService.SetAccessSiteLog(
    #         Convert.ToInt32(objSiteAccessListRS.Rows[0]["AccessID"].ToString()),
    #         strSiteName
    #     );
    # }

    # ! If current user is not set, raise
    # if (string.IsNullOrEmpty(SessionDataService.GetSessionData("CurrUserID")))
    # {
    #     throw new Exception("User is not authorized on this site.");
    # }

    # context.Succeed(requirement);
    
    await session.set_session_data(request, RedisKeys.CURRENT_USER_ID, 81549)
    await session.set_session_data(request, RedisKeys.CURRENT_USER_LP_ID, 209349)
    
    # await session.set_session_data(request, RedisKeys.CURRENT_USER_LP_ID, 209354)
    
    return True
