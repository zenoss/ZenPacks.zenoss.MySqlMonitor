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
            name: 'host',
            fieldLabel: _t('Host'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'port',
            fieldLabel: _t('Port'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'user',
            fieldLabel: _t('User'),
            xtype: 'textfield'
            });

        idpanel.addField({
            name: 'password',
            fieldLabel: _t('Password'),
            xtype: 'textfield',
            inputType: 'password'
            });

        // idpanel.addField({
        //     name: 'connection_type',
        //     fieldLabel: _t('Connection type'),
        //     xtype: 'textfield'
        //     });

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
            id: 'connection_type-view',
            xtype: 'displayfield',
            name: 'connection_type',
            fieldLabel: _t('Connection type'),
            permission: 'Manage Device'
        });

        descriptionpanel.addField({
            id: 'version-view',
            xtype: 'displayfield',
            name: 'version',
            fieldLabel: _t('MySQL version'),
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
