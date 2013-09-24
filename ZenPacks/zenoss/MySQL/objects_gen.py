def get_monitoring_template(graphs, command):
    xml = []
    xml.append('''
  <object class="RRDTemplate" id="/zport/dmd/Devices/rrdTemplates/mysql" module="Products.ZenModel.RRDTemplate">
    <property id="targetPythonClass" mode="w" type="string">
      Products.ZenModel.Device
    </property>
    <tomanycont id="datasources">
      <object class="BasicDataSource" id="MySQL" module="Products.ZenModel.BasicDataSource">
        <property id="sourcetype" mode="w" select_variable="sourcetypes" type="selection">
          COMMAND
        </property>
        <property id="enabled" mode="w" type="boolean">
          True
        </property>
        <property id="eventClass" mode="w" type="string">
          /Cmd/Fail
        </property>
        <property id="severity" mode="w" type="int">
          3
        </property>
        <property id="commandTemplate" mode="w" type="string">
          /usr/bin/mysql -e 'show global status'
        </property>
        <property id="cycletime" mode="w" type="int">
          5
        </property>
        <property id="usessh" mode="w" type="boolean">
          True
        </property>
        <property id="parser" mode="w" type="string">
          ZenPacks.zenoss.MySQL.parsers.mysql_parser
        </property>
        <tomanycont id="datapoints">
    ''')
    for graph in graphs:
        for datapoint in graph[1]:
            xml.append('''
          <object class="RRDDataPoint" id="{datapoint}" module="Products.ZenModel.RRDDataPoint">
            <property id="rrdtype" mode="w" select_variable="rrdtypes" type="selection">
              GAUGE
            </property>
            <property id="isrow" mode="w" type="boolean">
              True
            </property>
          </object>
            '''.format(datapoint=get_id(datapoint)))
    xml.append('''
        </tomanycont>

      </object>
    </tomanycont>
    <tomanycont id="graphDefs">
    ''')
    for graph in graphs:
        xml.append('''
      <object class="GraphDefinition" id="{graph_id}" module="Products.ZenModel.GraphDefinition">
        <property id="height" mode="w" type="int">
          100
        </property>
        <property id="width" mode="w" type="int">
          500
        </property>
        <property id="log" mode="w" type="boolean">
          False
        </property>
        <property id="base" mode="w" type="boolean">
          False
        </property>
        <property id="miny" mode="w" type="int">
          -1
        </property>
        <property id="maxy" mode="w" type="int">
          -1
        </property>
        <property id="hasSummary" mode="w" type="boolean">
          True
        </property>
        <property id="sequence" mode="w" type="long">
          0
        </property>
        <tomanycont id="graphPoints">
        '''.format(graph_id=graph[0]))
        for datapoint in graph[1]:
            xml.append('''
          <object class="DataPointGraphPoint" id="{datapoint}" module="Products.ZenModel.DataPointGraphPoint">
            <property id="sequence" mode="w" type="long">
              1
            </property>
            <property id="lineType" mode="w" select_variable="lineTypes" type="selection">
              LINE
            </property>
            <property id="lineWidth" mode="w" type="long">
              1
            </property>
            <property id="stacked" mode="w" type="boolean">
              False
            </property>
            <property id="format" mode="w" type="string">
              %5.2lf%s
            </property>
            <property id="legend" mode="w" type="string">
              {legend}
            </property>
            <property id="limit" mode="w" type="long">
              -1
            </property>
            <property id="dpName" mode="w" type="string">
              MySQL_{datapoint}
            </property>
            <property id="cFunc" mode="w" type="string">
              AVERAGE
            </property>
          </object>
            '''.format(datapoint=get_id(datapoint), legend=datapoint))
        xml.append('''
        </tomanycont>
      </object>
        ''')
    xml.append('''
    </tomanycont>
  </object>
    ''')
    return ''.join(xml)

def get_id(datapoint):
    return datapoint.lower().replace(' ', '_')

print get_monitoring_template((
    ('Aborted', (
        'Aborted clients',
        'Aborted connects'
    )),
    ('Bytes', (
        'Bytes sent',
        'Bytes received',
    )),
    ('Commands', (
        'Com create db',
        'Com drop db',
        'Com alter db',
        'Com create table',
        'Com alter table',
        'Com drop table',
        'Com create user',
        'Com drop user',
        'Com call procedure',
        'Com commit',
        'Com check',
        'Com delete',
        'Com delete multi',
        'Com execute sql',
        'Com flush',
        'Com insert',
        'Com purge',
        'Com repair',
        'Com replace',
        'Com rollback',
        'Com select',
        'Com update',
        'Com update multi',
    )),
    ('Handler', (
        'Handler commit',
        'Handler delete',
        'Handler rollback',
        'Handler update',
        'Handler write',
        'Handler read first',
        'Handler read key',
        'Handler read last',
        'Handler read next',
        'Handler read prev',
        'Handler read rnd',
        'Handler read rnd next',
        'Handler savepoint',
    )),
    ('Key cache', (
        'Key reads',
        'Key writes',
    )),
    ('Open objects', (
        'Open files',
        'Open streams',
        'Open tables',
    )),
))

