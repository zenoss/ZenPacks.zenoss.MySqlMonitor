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

/* zMySQLConnectionString property */
Zenoss.zproperties.registerZPropertyType('miltilinecredentials', {xtype: 'miltilinecredentials'});

Ext.define("Zenoss.form.MultilineCredentials", {
    alias:['widget.miltilinecredentials'],
    extend:'Ext.form.Display',

    constructor: function(config) {
        // submitHandler: this.setValue,
        Zenoss.form.MultilineCredentials.superclass.constructor.apply(this, arguments);
     },

    initComponent: function() {
        this.grid = this.childComponent = Ext.create('Ext.grid.Panel', {
            hideHeaders: true,
            columns: [{
                dataIndex: 'value',
                flex: 1,
                renderer: function(value) {
                    var bits = value.split(":");
                    if (bits.length == 3)
                        return bits[0]+ ":***:" + bits[2]
                    else
                        return "ERROR: Invalid connection string!";
                }
            }],

            store: {
                fields: ['value'],
                data: []
            },

            height: this.height || 150,
            width: this.width || 150,
            
            tbar: [{
                itemId: 'user',
                xtype:"textfield",
                scope: this,
                width: 50,
                value: "root",
            },{
                itemId: 'password',
                xtype:"password",
                scope: this,
                width: 50,
                value: "",
            },{
                itemId: 'port',
                xtype:"textfield",
                scope: this,
                width: 50,
                value: "3306",
            },{
                text: 'Add',
                scope: this,
                handler: function() {
                    var user = this.grid.down('#user');
                    var password = this.grid.down('#password');
                    var port = this.grid.down('#port');

                    var value = user.value+":"+password.value+":"+port.value+";";
                    if (user.value !== "") {
                        this.grid.getStore().add({value: value});
                    }

                    user.setValue("");
                    password.setValue("");
                    port.setValue("");
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
 });


}());
