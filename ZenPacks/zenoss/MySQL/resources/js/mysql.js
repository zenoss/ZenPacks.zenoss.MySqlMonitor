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
ZC.registerName('MySQLDatabase', _t('MySQL Database'), _t('MySQL Database'));

var add_mysqlserver = new Zenoss.Action({
    text: _t('Add MySQL Server') + '...',
    id: 'add_myslqserver-item',
    permission: 'Manage DMD',
    handler: function(btn, e){
        var win = new Zenoss.dialog.CloseDialog({
            width: 400,
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
                    name: 'host',
                    fieldLabel: _t('Host'),
                    id: 'add_myslqserver-host',
                    width: 260,
                    allowBlank: false
                }, {
                    xtype: 'textfield',
                    name: 'port',
                    fieldLabel: _t('Port'),
                    id: 'add_myslqserver-port',
                    width: 260,
                    allowBlank: true,
                }, {
                    xtype: 'textfield',
                    name: 'user',
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
                        
                        Zenoss.remote.MySQLRouter.add_mysqlserver(
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
