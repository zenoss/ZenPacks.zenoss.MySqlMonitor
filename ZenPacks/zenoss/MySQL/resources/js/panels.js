/*****************************************************************************
 *
 * Copyright (C) Zenoss, Inc. 2013, all rights reserved.
 *
 * This content is made available according to terms specified in
 * License.zenoss under the directory where your Zenoss product is installed.
 *
 ****************************************************************************/

(function(){

var ZC = Ext.ns('Zenoss.component');
var ZD = Ext.ns('Zenoss.devices');

/* pingStatus renderer override */
var upDownTemplate = new Ext.Template(
    '<span class="status-{0}{2}">{1}</span>');
upDownTemplate.compile();

Ext.apply(Zenoss.render, {
    linkFromSubgrid: function(value, metaData, record) {
        if (this.subComponentGridPanel) {
            return Zenoss.render.link(record.data.uid, null, value);
        } else {
            return value;
        }
    },
    table_pingStatus: function(value) {
        if (value) {
            result = (value == "OK")? 'Up' : 'Down';
            return upDownTemplate.apply([result.toLowerCase(), value]);
        }
    }
});

/* MySQLDatabase */
ZC.MySQLDatabasePanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'MySQLDatabase',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'size'},
                {name: 'table_count'},
                {name: 'stored_procedure_count'},
                {name: 'stored_function_count'},
                {name: 'character_set'},
                {name: 'collation'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
            },{                
                id: 'table_count',
                dataIndex: 'table_count',
                header: _t('Tables'),
            },{                 
                id: 'stored_procedure_count',
                dataIndex: 'stored_procedure_count',
                header: _t('Stored procedures'),
            },{                
                id: 'stored_function_count',
                dataIndex: 'stored_function_count',
                header: _t('Stored functions'),
            },{ 
                id: 'character_set',
                dataIndex: 'character_set',
                header: _t('Character set'),
            },{ 
                id: 'collation',
                dataIndex: 'collation',
                header: _t('Collation'),
            },{      
                id: 'size',
                dataIndex: 'size',
                header: _t('Size'),
            },{ 
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                renderer: Zenoss.render.pingStatus,
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 60
            }]
        });
        ZC.MySQLDatabasePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('MySQLDatabasePanel', ZC.MySQLDatabasePanel);

/* MySQLTable */
ZC.MySQLTablePanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'MySQLTable',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'database'},
                {name: 'engine'},
                {name: 'table_type'},
                {name: 'table_collation'},
                {name: 'table_rows'},
                {name: 'size'},
                {name: 'table_status'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.linkFromSubgrid,
            },{
                id: 'database',
                dataIndex: 'database',
                header: _t('Database'),
                renderer: Zenoss.render.linkFromGrid,
            },{                 
                id: 'engine',
                dataIndex: 'engine',
                header: _t('Engine'),
            },{                
                id: 'table_type',
                dataIndex: 'table_type',
                header: _t('Type'),
            },{                
                id: 'table_collation',
                dataIndex: 'table_collation',
                header: _t('Collation'),
            },{                 
                id: 'table_rows',
                dataIndex: 'table_rows',
                header: _t('Rows'),
            },{             
                id: 'size',
                dataIndex: 'size',
                header: _t('Size'),
            },{            
                id: 'table_status',
                dataIndex: 'table_status',
                header: _t('Status'),
                renderer: Zenoss.render.table_pingStatus,
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 60
            }]
        });
        ZC.MySQLTablePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('MySQLTablePanel', ZC.MySQLTablePanel);

/* MySQLStoredProcedure */
ZC.MySQLStoredProcedurePanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'MySQLStoredProcedure',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'database'},
                {name: 'body'},
                {name: 'security_type'},
                {name: 'created'},
                {name: 'last_altered'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.linkFromSubgrid,
            },{
                id: 'database',
                dataIndex: 'database',
                header: _t('Database'),
                renderer: Zenoss.render.linkFromGrid,
            },{           
                id: 'body',
                dataIndex: 'body',
                header: _t('Body'),
            },{          
                id: 'security_type',
                dataIndex: 'security_type',
                header: _t('Security type'),
            },{          
                id: 'created',
                dataIndex: 'created',
                header: _t('Created on'),
            },{          
                id: 'last_altered',
                dataIndex: 'last_altered',
                header: _t('Altered on'),
            },{
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                renderer: Zenoss.render.pingStatus,
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 60
            }]
        });
        ZC.MySQLStoredProcedurePanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('MySQLStoredProcedurePanel', ZC.MySQLStoredProcedurePanel);

/* MySQLStoredFunction */
ZC.MySQLStoredFunctionPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'MySQLStoredFunction',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'database'},
                {name: 'body'},
                {name: 'security_type'},
                {name: 'created'},
                {name: 'last_altered'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.linkFromSubgrid,
            },{
                id: 'database',
                dataIndex: 'database',
                header: _t('Database'),
                renderer: Zenoss.render.linkFromGrid,
            },{           
                id: 'body',
                dataIndex: 'body',
                header: _t('Body'),
            },{          
                id: 'security_type',
                dataIndex: 'security_type',
                header: _t('Security type'),
            },{          
                id: 'created',
                dataIndex: 'created',
                header: _t('Created on'),
            },{          
                id: 'last_altered',
                dataIndex: 'last_altered',
                header: _t('Altered on'),
            },{
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                renderer: Zenoss.render.pingStatus,
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 60
            }]
        });
        ZC.MySQLStoredFunctionPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('MySQLStoredFunctionPanel', ZC.MySQLStoredFunctionPanel);

/* MySQLProcess */
ZC.MySQLProcessPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            autoExpandColumn: 'name',
            componentType: 'MySQLProcess',
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'user'},
                {name: 'host'},
                {name: 'db'},
                {name: 'command'},
                {name: 'time'},
                {name: 'state'},
                {name: 'process_info'},
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Process ID'),
                renderer: Zenoss.render.linkFromSubgrid,
            },{                               
                id: 'user',
                dataIndex: 'user',
                header: _t('User'),
            },{               
                id: 'host',
                dataIndex: 'host',
                header: _t('Host'),
            },{               
                id: 'db',
                dataIndex: 'db',
                header: _t('Database'),
            },{               
                id: 'command',
                dataIndex: 'command',
                header: _t('Command'),
            },{               
                id: 'time',
                dataIndex: 'time',
                header: _t('Time'),
            },{               
                id: 'state',
                dataIndex: 'state',
                header: _t('State'),
            },{               
                id: 'process_info',
                dataIndex: 'process_info',
                header: _t('Info'),
            },{
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                renderer: Zenoss.render.pingStatus,
                width: 50
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                width: 60
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 60
            }]
        });
        ZC.MySQLProcessPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('MySQLProcessPanel', ZC.MySQLProcessPanel);

/* Subcomponent Panels */
/* MySQLTable */
Zenoss.nav.appendTo('Component', [{
    id: 'database_tables',
    text: _t('Tables'),
    xtype: 'MySQLTablePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
         switch (navpanel.refOwner.componentType) {
            case 'MySQLDatabase': return true;
            default: return false;
         }
    },
    setContext: function(uid) {
        ZC.MySQLTablePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

/* MySQLStoredProcedure */
Zenoss.nav.appendTo('Component', [{
    id: 'database_stored_procedures',
    text: _t('Stored procedures'),
    xtype: 'MySQLStoredProcedurePanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
         switch (navpanel.refOwner.componentType) {
            case 'MySQLDatabase': return true;
            default: return false;
         }
    },
    setContext: function(uid) {
        ZC.MySQLStoredProcedurePanel.superclass.setContext.apply(this, [uid]);
    }
}]);

/* MySQLStoredFunction */
Zenoss.nav.appendTo('Component', [{
    id: 'database_stored_functions',
    text: _t('Stored functions'),
    xtype: 'MySQLStoredFunctionPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
         switch (navpanel.refOwner.componentType) {
            case 'MySQLDatabase': return true;
            default: return false;
         }
    },
    setContext: function(uid) {
        ZC.MySQLStoredFunctionPanel.superclass.setContext.apply(this, [uid]);
    }
}]);

/* Overview Panel Override */
Ext.onReady(function(){
    var REMOTE = Zenoss.remote.MySQLRouter;

    Ext.define("Zenoss.devices.DeviceClassDataStore", {
        extend:"Zenoss.NonPaginatedStore",
        constructor: function(config) {
            config = config || {};
            var router = config.router || Zenoss.remote.DeviceRouter;
            Ext.applyIf(config, {
                root: 'deviceClasses',
                totalProperty: 'totalCount',
                model: 'Zenoss.model.Name',
                directFn: Zenoss.remote.DeviceRouter.getDeviceClasses
            });
            this.callParent([config]);
        }
    });

    Ext.define("Zenoss.devices.DeviceClassCombo", {
        extend:"Zenoss.form.SmartCombo",
        alias: ['widget.deviceclasscombo'],
        constructor: function(config) {
            var store = (config||{}).store || new ZD.DeviceClassDataStore();
            config = Ext.applyIf(config||{}, {
                displayField: 'name',
                valueField: 'name',
                store: store,
                width: 300,
                minListWidth: 250,
                editable: true,
                typeAhead: true,
                forceSelection: true,
                allowBlank: true,
                listConfig: {
                    resizable: true
                }
            });
            this.callParent([config]);
        }
    });

    function editDeviceClassInfo(vals, uid) {
        function name(uid) {
            if (!uid) {
                return 'Unknown';
            }

            if (!Ext.isString(uid)) {
                uid = uid.uid;
            }

            return uid.split('/').reverse()[0];
        }

        var FIELDWIDTH = 300;

        var win = new Zenoss.FormDialog({
            autoHeight: true,
            width: FIELDWIDTH + 90,
            title: _t('Edit Device Classes for Discovered Instances'),
            items: [{
                xtype: 'container',
                layout: 'anchor',
                autoHeight: true,
                items: [linuxDeviceClass, windowsDeviceClass]
            }],
            buttons: [{
                text: _t('Save'),
                ref: '../savebtn',
                xtype: 'DialogButton',
                id: 'win-save-button',
                disabled: Zenoss.Security.doesNotHavePermission('Manage Device'),
                handler: function(btn){
                    var form = btn.refOwner.editForm.getForm(),
                        vals = form.getValues();
                    Ext.apply(vals, {uid:uid});
                    REMOTE.set_device_class_info(vals, function(r) {
                        Ext.getCmp('device_overview').load();
                        win.destroy();
                    });
                }
            },{
                text: _t('Cancel'),
                xtype: 'DialogButton',
                id: 'win-cancel-button',
                handler: function(btn){
                    win.destroy();
                }
            }]
        });

        win.show();
        win.doLayout();
    }

    var DEVICE_SUMMARY_PANEL = 'deviceoverviewpanel_summary';
    var DEVICE_ID_PANEL = 'deviceoverviewpanel_idsummary';
    var DEVICE_DESCRIPTION_PANEL = 'deviceoverviewpanel_descriptionsummary';
    var DEVICE_CUSTOM_PANEL = 'deviceoverviewpanel_customsummary';
    var DEVICE_SNMP_PANEL = 'deviceoverviewpanel_snmpsummary';
    
    /* Summary Panel Override */
    Ext.ComponentMgr.onAvailable(DEVICE_SUMMARY_PANEL, function(){
        var summarypanel = Ext.getCmp(DEVICE_SUMMARY_PANEL);
        summarypanel.hide();
        });

    /* ID Panel Override */
    Ext.ComponentMgr.onAvailable(DEVICE_ID_PANEL, function(){
        var idpanel = Ext.getCmp(DEVICE_ID_PANEL);
        
        idpanel.removeField('serialNumber');
        idpanel.removeField('tagNumber');

        idpanel.addField({
            name: 'manageIp',
            fieldLabel: _t('IP'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'zCommandPort',
            fieldLabel: _t('Port'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'zCommandUsername',
            fieldLabel: _t('User'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'zCommandPassword',
            fieldLabel: _t('Password'),
            xtype: 'textfield',
            inputType: 'password'
            });

        idpanel.addField({
            name: 'cmd',
            fieldLabel: _t('SSH command tool'),
            xtype: 'textfield',
            inputType: 'textfield'
            });

        // idpanel.addField({
        //     name: 'version',
        //     fieldLabel: _t('MySQL version'),
        //     xtype: 'textfield'
        //     });

        });

    /* Description Panel Override */
    Ext.ComponentMgr.onAvailable(DEVICE_DESCRIPTION_PANEL, function(){
        var descriptionpanel = Ext.getCmp(DEVICE_DESCRIPTION_PANEL);

        descriptionpanel.defaultType = 'devformpanel';
        
        descriptionpanel.removeField('rackSlot');
        descriptionpanel.removeField('hwManufacturer');
        descriptionpanel.removeField('hwModel');
        descriptionpanel.removeField('osManufacturer');
        descriptionpanel.removeField('osModel');

        descriptionpanel.addField({
            id: 'version-view',
            xtype: 'displayfield',
            name: 'version',
            fieldLabel: _t('MySQL version'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'size-view',
            xtype: 'displayfield',
            name: 'size',
            fieldLabel: _t('Size'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'data_size-view',
            xtype: 'displayfield',
            name: 'data_size',
            fieldLabel: _t('Data Size'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'index_size-view',
            xtype: 'displayfield',
            name: 'index_size',
            fieldLabel: _t('Index size'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'percent_full_table_scans-view',
            xtype: 'displayfield',
            name: 'percent_full_table_scans',
            fieldLabel: _t('Percentage of full table scans'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'master_status-view',
            xtype: 'displayfield',
            name: 'master_status',
            fieldLabel: _t('Master status'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'slave_status-view',
            xtype: 'displayfield',
            name: 'slave_status',
            fieldLabel: _t('Slave status'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'first_seen-view',
            xtype: 'displayfield',
            name: 'first_seen',
            fieldLabel: _t('First Seen'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'model_time-view',
            xtype: 'displayfield',
            name: 'model_time',
            fieldLabel: _t('Model Time'),
            permission: 'Manage Device'
        });
    });

    /* SNMP Panel Override */
    Ext.ComponentMgr.onAvailable(DEVICE_SNMP_PANEL, function(){
        var snmppanel = Ext.getCmp(DEVICE_SNMP_PANEL);
        snmppanel.hide();
    });

});

})();
