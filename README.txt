MySqlMonitor Summary
--------------------

MySqlMonitor provides a method for pulling performance metrics from the MySQL
database server (http://www.mysql.com/) directly into Zenoss without requiring
the use of an agent. This is accomplished by utilizing the MySQL client library
to connect to the database remotely.

The following metrics will be collected and graphed for MySQL server.

    * Command Statistics (SELECT, INSERT, UPDATE, DELETE)
    * Select Statistics (Scan, Range Check, Range Join, Full Join)
    * Handler Statistics (Keyed & Unkeyed Reads, Writes, Updates, Deletes)
    * Network Traffic (Received & Sent)


MySqlMonitor Installation & Usage
---------------------------------

Follow these steps to setup your MySQL server to allow Zenoss to read
performance data from the system tables. Fortunately to collect statistics the
user you create will require NO privileges at all, it will just need to be a
valid user.

    1. Connect to the MySQL database using the MySQL client.

        mysql -u root

        ... or if there is a MySQL root password ...

        mysql -u root -p

    2. Create a user for Zenoss to use. The username "zenoss" is recommended.

        mysql> CREATE USER zenoss IDENTIFIED BY 'zenossPassword';
        Query OK, 0 rows affected (0.00 sec)

    3. Edit the zMySqlUsername and zMySqlPassword zProperties for the device(s)
       within Zenoss that you intend to monitor MySQL on.

    4. Bind the MySQL template to the same device(s).

Pay particular attention to the MySQL Version 5+ setting in the datasource.  If
you are monitoring pre-v5 installations of MySQL then be sure to set this value
to False.  If you are monitoring both pre v5 and v5+ installations then create
two templates, one for MySQL installations earlier than v5 and another for
those after.
