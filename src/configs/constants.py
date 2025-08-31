class DBTables:
    USERS       = "users"

class  DBConfig:
    SCHEMA_NAME = "public"
    BASE_ARGS   = { "schema": SCHEMA_NAME }
    
class RedisKeys:
    CURRENT_USER_ID = 'CurrUserId'
    TRUE_USER_ID = 'TrueUserID'
    
    CURRENT_USER_LP_ID = 'CurrUserLPID'
    
    PERMISSION_MYSEQUOIA_CAPITAL = 'PermissionMySequoiaCapital'
    
    MY_SC_VIEW_FSTMT = "mySCView-FStmt"
    MY_SC_VIEW_FSTMTMC = "mySCView-FStmtMC"
    MY_SC_VIEW_SANNUAL = "mySCView-SAnnual"
    MY_SC_VIEW_AUD_FS = "mySCView-AudFS"