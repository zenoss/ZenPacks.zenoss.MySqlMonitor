# Result containing slave status data
RESULT1 = [{
    'slave': ({
        'Replicate_Wild_Do_Table': '',
        'Master_SSL_CA_Path': '',
        'Last_Error': '',
        'Until_Log_File': '',
        'Seconds_Behind_Master': None,
        'Master_User': 'zenoss',
        'Master_Port': 3306L,
        'Until_Log_Pos': 0L,
        'Master_Log_File': 'mysql-bin.000003 ',
        'Read_Master_Log_Pos': 98L,
        'Replicate_Do_DB': '',
        'Master_SSL_Verify_Server_Cert': 'No',
        'Exec_Master_Log_Pos': 98L,
        'Replicate_Ignore_Server_Ids': '',
        'Replicate_Ignore_Table': '',
        'Master_Server_Id': 0L,
        'Relay_Log_Space': 233L,
        'Last_SQL_Error': '',
        'Relay_Master_Log_File': 'mysql-bin.000003 ',
        'Master_SSL_Allowed': 'No',
        'Master_SSL_CA_File': '',
        'Slave_IO_State': '',
        'Relay_Log_File': 'localhost-relay-bin.000001',
        'Replicate_Ignore_DB': '',
        'Last_IO_Error': '',
        'Until_Condition': 'None',
        'Replicate_Do_Table': '',
        'Last_Errno': 0L,
        'Master_Host': '127.0.0.1',
        'Master_SSL_Key': '',
        'Skip_Counter': 0L,
        'Slave_SQL_Running': 'No',
        'Relay_Log_Pos': 4L,
        'Master_SSL_Cert': '',
        'Last_IO_Errno': 0L,
        'Slave_IO_Running': 'No',
        'Connect_Retry': 60L,
        'Last_SQL_Errno': 0L,
        'Replicate_Wild_Ignore_Table': '',
        'Master_SSL_Cipher': ''
    },),
    'db': ({
        'title': 'information_schema',
        'default_collation_name': 'utf8_general_ci',
        'index_size': 9216,
        'table_count': 40L,
        'data_size': 0,
        'default_character_set_name': 'utf8',
        'size': 9216
    },),
    'server': (
        {'variable_value': '0', 'variable_name': 'HANDLER_READ_FIRST'},
        {'variable_value': '127', 'variable_name': 'HANDLER_READ_KEY'},
        {'variable_value': 'OFF', 'variable_name': 'SLAVE_RUNNING'}
    ),
    'master': (),
    'server_size': ({
        'index_size': 4143104,
        'data_size': 53423729,
        'size': 57566833
    },),
    'id': 'root_3306'}
]
# -------------------------------------------------------------------------
# Server results
SERVER_STATUS1 = (
    {'variable_value': '0', 'variable_name': 'HANDLER_READ_FIRST'},
    {'variable_value': '127', 'variable_name': 'HANDLER_READ_KEY'},
)
SERVER_STATUS2 = (
    {'variable_value': '127', 'variable_name': 'HANDLER_READ_FIRST'},
    {'variable_value': '0', 'variable_name': 'HANDLER_READ_KEY'},
)
SERVER_STATUS3 = (
    {'variable_value': '10', 'variable_name': 'HANDLER_READ_FIRST'},
    {'variable_value': '20', 'variable_name': 'HANDLER_READ_KEY'},
)
# -------------------------------------------------------------------------
# Master results
MASTER_STATUS1 = ({
    'File': 'mysql-bin.000002',
    'Position': '107',
    'Binlog_Do_DB': '',
    'Binlog_Ignore_DB': '',
},)
MASTER_STATUS2 = ()
# -------------------------------------------------------------------------
# Slave results
SLAVE_STATUS1 = ({
    'Replicate_Wild_Do_Table': '',
    'Master_SSL_CA_Path': '',
    'Last_Error': '',
    'Until_Log_File': '',
    'Seconds_Behind_Master': 10,
    'Master_User': 'zenoss',
    'Master_Port': 3306L,
    'Until_Log_Pos': 0L,
    'Master_Log_File': 'mysql-bin.000003 ',
    'Read_Master_Log_Pos': 98L,
    'Replicate_Do_DB': '',
    'Master_SSL_Verify_Server_Cert': 'No',
    'Exec_Master_Log_Pos': 98L,
    'Replicate_Ignore_Server_Ids': '',
    'Replicate_Ignore_Table': '',
    'Master_Server_Id': 0L,
    'Relay_Log_Space': 233L,
    'Last_SQL_Error': '',
    'Relay_Master_Log_File': 'mysql-bin.000003 ',
    'Master_SSL_Allowed': 'No',
    'Master_SSL_CA_File': '',
    'Slave_IO_State': '',
    'Relay_Log_File': 'localhost-relay-bin.000001',
    'Replicate_Ignore_DB': '',
    'Last_IO_Error': '',
    'Until_Condition': 'None',
    'Replicate_Do_Table': '',
    'Last_Errno': 0L,
    'Master_Host': '127.0.0.1',
    'Master_SSL_Key': '',
    'Skip_Counter': 0L,
    'Slave_SQL_Running': 'No',
    'Relay_Log_Pos': 4L,
    'Master_SSL_Cert': '',
    'Last_IO_Errno': 0L,
    'Slave_IO_Running': 'No',
    'Connect_Retry': 60L,
    'Last_SQL_Errno': 0L,
    'Replicate_Wild_Ignore_Table': '',
    'Master_SSL_Cipher': ''
},)
SLAVE_STATUS2 = ()
