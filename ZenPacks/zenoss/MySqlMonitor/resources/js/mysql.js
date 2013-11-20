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

ZC.registerName('MySQLServer', _t('MySQL Server'), _t('MySQL Servers'));
ZC.registerName('MySQLDatabase', _t('MySQL Database'), _t('MySQL Databases'));

/* helper function to get the number of stars returned for password */
String.prototype.repeat = function(num) {
    return new Array(isNaN(num)? 1 : ++num).join(this);
}

/* Zenoss.ConfigProperty.Grid override */
Ext.define("MySQL.ConfigProperty.Grid", {
    alias: ['widget.configpropertygrid'],
    extend:"Zenoss.ConfigProperty.Grid",
    constructor: function(config) {
        Ext.applyIf(config, {
            columns: [{
                header: _t("Is Local"),
                id: 'islocal',
                dataIndex: 'islocal',
                width: 60,
                sortable: true,
                filter: false,
                renderer: function(value){
                    if (value) {
                        return 'Yes';
                    }
                    return '';
                }
            },{
                id: 'category',
                dataIndex: 'category',
                header: _t('Category'),
                sortable: true
            },{
                id: 'id',
                dataIndex: 'id',
                header: _t('Name'),
                width: 200,
                sortable: true
            },{
                id: 'value',
                dataIndex: 'valueAsString',
                header: _t('Value'),
                flex: 1,
                width: 180,
                renderer: function(v, row, record) {
                    // renderer for zMySQLConnectionString
                    if (record.internalId == 'zMySQLConnectionString' &&
                        record.get('value') !== "") {
                        return this.__renderMySQLConnectionString(record.get('value'));
                    }

                    if (Zenoss.Security.doesNotHavePermission("zProperties Edit") &&
                        record.data.id == 'zSnmpCommunity') {
                        return "*******";
                    }
                    return v;
                },
                sortable: false
            },{
                id: 'path',
                dataIndex: 'path',
                header: _t('Path'),
                width: 200,
                sortable: true
            }]
        });
        this.callParent(arguments);
    },

    __renderMySQLConnectionString: function(value) {
        result = [];
        Ext.each(value, function (value) {
            try {
                var v = JSON.parse(value);
                result.push(v.user + ":" + "*".repeat(v.passwd.length) + ":" + v.port);
            } catch (err) {
                result.push("ERROR: Invalid connection string!");
            }
        })
        return result.join(';');
    }
});

/* zMySQLConnectionString property */
Zenoss.zproperties.registerZPropertyType('multilinecredentials', {xtype: 'multilinecredentials'});

Ext.define("Zenoss.form.MultilineCredentials", {
    alias:['widget.multilinecredentials'],
    extend: 'Ext.form.field.Base',
    mixins: {
        field: 'Ext.form.field.Field'
    },

    constructor: function(config) {
        config = Ext.applyIf(config || {}, {
            editable: true,
            allowBlank: true,
            submitValue: true,
            triggerAction: 'all',
        });
        config.fieldLabel = "MySQL connection credentials";
        Zenoss.form.MultilineCredentials.superclass.constructor.call(this, config);
    },

    initComponent: function() {
        this.grid = this.childComponent = Ext.create('Ext.grid.Panel', {
            hideHeaders: true,
            columns: [{
                dataIndex: 'value',
                flex: 1,
                renderer: function(value) {
                    try {
                        value = JSON.parse(value);
                        return value.user + ":" + "*".repeat(value.passwd.length) + ":" + value.port;
                    } catch (err) {
                        return "ERROR: Invalid connection string!";
                    }
                }
            }],

            store: {
                fields: ['value'],
                data: []
            },

            height: this.height || 150,
            width: 300,
            
            tbar: [{
                itemId: 'user',
                xtype: "textfield",
                scope: this,
                width: 70,
                emptyText:'User',
            },{
                itemId: 'password',
                xtype: "password",
                scope: this,
                width: 70,
                emptyText:'Password',
                value: '' //to avoid undefined value
            },{
                itemId: 'port',
                xtype: "textfield",
                scope: this,
                width: 50,
                emptyText:'Port',
                value: '' //to avoid undefined value
            },{
                text: 'Add',
                scope: this,
                handler: function() {
                    var user = this.grid.down('#user');
                    var password = this.grid.down('#password');
                    var port = this.grid.down('#port');

                    var value = {
                        'user': user.value,
                        'passwd': password.value, 
                        'port': port.value
                    };
                    if (user.value) {
                        this.grid.getStore().add({value: JSON.stringify(value)});
                    }

                    user.setValue("");
                    password.setValue("");
                    port.setValue("");

                    this.checkChange();
                }
            },{
                text: "Remove",
                itemId: 'removeButton',
                disabled: true, // initial state
                scope: this,
                handler: function() {
                    var grid = this.grid,
                        selModel = grid.getSelectionModel(),
                        store = grid.getStore();
                    store.remove(selModel.getSelection());
                    this.checkChange();
                }
            }],

            listeners: {
                scope: this,
                selectionchange: function(selModel, selection) {
                    var removeButton = this.grid.down('#removeButton');
                    removeButton.setDisabled(Ext.isEmpty(selection));
                }
            }
        });

        this.callParent(arguments);
    },

    // --- Rendering ---
    // Generates the child component markup
    getSubTplMarkup: function() {
        // generateMarkup will append to the passed empty array and return it
        var buffer = Ext.DomHelper.generateMarkup(this.childComponent.getRenderTree(), []);
        // but we want to return a single string
        return buffer.join('');
    },

    // Regular containers implements this method to call finishRender for each of their
    // child, and we need to do the same for the component to display smoothly
    finishRenderChildren: function() {
        this.callParent(arguments);
        this.childComponent.finishRender();
    },

    // --- Resizing ---
    onResize: function(w, h) {
        this.callParent(arguments);
        this.childComponent.setSize(w - this.getLabelWidth(), h);
    },

    // --- Value handling ---
    setValue: function(values) {
        var data = [];
        if (values) {
            Ext.each(values, function(value) {
                data.push({value: value});
            });
        }
        this.grid.getStore().loadData(data);
    },

    getValue: function() {
        var data = [];
        this.grid.getStore().each(function(record) {
            data.push(record.get('value'));
        });
        return data;        
    },

    getSubmitValue: function() {
        return this.getValue();
    },
});

}());
