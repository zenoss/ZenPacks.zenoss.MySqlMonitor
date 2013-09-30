##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

TB_QUERY = """
    SELECT table_schema, table_name, engine, table_type, table_collation, 
        table_rows, (data_length + index_length) size, data_length, index_length
    FROM information_schema.TABLES;
"""

TB_STATUS_QUERY = """
    mysqlcheck -A;
"""

DB_QUERY = """
    SELECT schema_name, default_character_set_name, default_collation_name, 
        size, data_length, index_length
    FROM information_schema.schemata LEFT JOIN 
        (SELECT table_schema, sum(data_length + index_length) size, 
            sum(data_length) data_length, sum(index_length) index_length
        FROM information_schema.TABLES 
        GROUP BY table_schema) as sizes
    ON schema_name = sizes.table_schema;
"""

ROUTINE_QUERY = """
    SELECT routine_schema, routine_name, routine_type, 
        routine_body, routine_definition, external_language, 
        security_type, created, last_altered
    FROM information_schema.ROUTINES;
"""

PROCESS_QUERY = """
    SHOW PROCESSLIST;
"""

SERVER_QUERY = """
    SELECT variable_name, variable_value  
    FROM information_schema.SESSION_STATUS  
    WHERE variable_name IN ("Handler_read_first", "Handler_read_key", 
        "Slave_running");
"""

SERVER_SIZE_QUERY = """
    SELECT sum(data_length + index_length) size, 
        sum(data_length) data_length, sum(index_length) index_length 
    FROM information_schema.TABLES;
"""

MASTER_QUERY = """
    SHOW MASTER STATUS;
"""

SLAVE_QUERY = """
    SHOW SLAVE STATUS\G;
"""

SPLITTER_QUERY = """
    SELECT "splitter";
"""


def tab_parse(query_result):
    """Parse the result of the mysql query.

    @param query_result: result of mysql query
    @type result: list of str
    @return: dict with row number as a key and dict of 
    mysql query parameters and their values as a value    
    """

    result = {}
    key = 0
    headers = [header.lower() for header in query_result[0].split('\t')]

    # Parsing the table result
    for line in query_result[1:]:
        line = line.split('\t')
        properties = {}
        for i, header in enumerate(headers):
            properties[header] = line[i]

        result[key] = properties
        key +=1 

    return result
