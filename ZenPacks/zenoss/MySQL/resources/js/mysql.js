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

ZC.registerName('MySQLServer', _t('MySQL Server'), _t('MySQL Server'));
ZC.registerName('MySQLDatabase', _t('Database'), _t('Databases'));
ZC.registerName('MySQLStoredProcedure', _t('Stored procedure'), _t('Stored procedures'));
ZC.registerName('MySQLStoredFunction', _t('Stored function'), _t('Stored functions'));
ZC.registerName('MySQLTable', _t('Table'), _t('Tables'));
ZC.registerName('MySQLProcess', _t('Process'), _t('Processes'));

var add_mysqlserver = new Zenoss.Action({
    text: _t('Add MySQL Server') + '...',
    id: 'add_myslqserver-item',
    permission: 'Manage DMD',
    handler: function(btn, e){
        var win = new Zenoss.dialog.CloseDialog({
            width: 300,
            title: _t('Add MySQL server'),
            items: [{
                xtype: 'form',
                buttonAlign: 'left',
                monitorValid: true,
                labelAlign: 'top',
                footerStyle: 'padding-left: 0',
                border: false,
                items: [{
                    xtype: 'textfield',
                    name: 'device_name',
                    fieldLabel: _t('Server Name'),
                    id: 'add_myslqserver-devicename',
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'host',
                    value: 'localhost',
                    fieldLabel: _t('Host'),
                    id: 'add_myslqserver-host',
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'port',
                    value: '22',
                    fieldLabel: _t('Port'),
                    id: 'add_myslqserver-port',
                    width: 260,
                    allowBlank: true,
                }, {
                    xtype: 'textfield',
                    name: 'user',
                    value: 'root',
                    fieldLabel: _t('User'),
                    id: 'add_myslqserver-user',
                    width: 260,
                    allowBlank: false,
                }, {
                    xtype: 'textfield',
                    name: 'password',
                    inputType: 'password',
                    fieldLabel: _t('Password'),
                    id: 'add_mysqlserver-password',
                    width: 260,
                    allowBlank: true
                }, {
                    xtype: 'combo',
                    width: 260,
                    name: 'connection_type',
                    fieldLabel: _t('Connection type'),
                    id: 'add_mysqlserver-connection-type',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        id: 0,
                        fields: [
                            'name'
                        ],
                        data: [['MySQL'], ['Script via SSH']]  // data is local
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            component.setValue('Script via SSH');
                        }
                    }
                }, {
                    xtype: 'combo',
                    width: 260,
                    name: 'version',
                    fieldLabel: _t('MySQL version'),
                    id: 'add_mysqlserver-version',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        id: 0,
                        fields: [
                            'name'
                        ],
                        data: [['5.1'], ['5.5'], ['5.6'], ['5.7']]  // data is local
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            component.setValue('5.5');
                        }
                    }
                }, {
                    xtype: 'combo',
                    width: 260,
                    name: 'collector',
                    fieldLabel: _t('Collector'),
                    id: 'add_mysqlserver-collector',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        data: Zenoss.env.COLLECTORS,
                        fields: ['name']
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            var index = component.store.find('name', 'localhost');
                            if (index >= 0) {
                                component.setValue('localhost');
                            }
                        }
                    }
                }],
                buttons: [{
                    xtype: 'DialogButton',
                    id: 'add_myslqserver-submit',
                    text: _t('Add'),
                    formBind: true,
                    handler: function(b) {
                        var form = b.ownerCt.ownerCt.getForm();
                        var opts = form.getFieldValues();
                        
                        Zenoss.remote.MySQLRouter.add_device(
                            opts,
                            function(response) {
                                if(response.success){
                                    new Zenoss.dialog.SimpleMessageDialog({
                                        message: _t('Add MySQL server job submitted'),
                                        buttons: [{
                                            xtype: 'DialogButton',
                                            text: _t('OK')
                                        }]
                                        }).show();
                                    }
                                else {
                                    new Zenoss.dialog.SimpleMessageDialog({
                                        message: response.msg,
                                        buttons: [{
                                            xtype: 'DialogButton',
                                            text: _t('OK')
                                            }]
                                        }).show();
                                    }
                                }
                            );
                        }
                    }, Zenoss.dialog.CANCEL]
                }]
            });
        win.show();
    }
});


var ZE = Ext.ns('Zenoss.extensions');

ZE.adddevice = ZE.adddevice instanceof Array ? ZE.adddevice : [];
ZE.adddevice.push(add_mysqlserver);
}());
