# Mpay:

![Alt text]("https://github.com/yezyilomo/Mpay/blob/master/mpay_logo.png")


 Odoo application for online payment through mobile SMS based services in eCommerce site.

# Features

  -Enable a company to record all transactions done through mobile payment

  -Enable clients to do payment of products in odoo ecommerce by using mobile payment services like M-Pesa, Tigo-Pesa, Airtel-Money, Hallo-Pesa, etc..

  -Include payments done through Mobile transactions in odoo reports


# Resources
  -Smartphone with android OS( for SMS gateway app to be installed)

  -Server for launching the system

# A walk through expected application

  -Client access ecommerce site

  -Client select a product he/she want to buy

  -Client place an order for that product

  -Client obtain a number for doing payment from the ecommerce site after placing an order as publishe by his saler

  -Client go to pay for the product he/she ordered through his/her mobile phone and specific services provider(eg Vodacom, Tigo, etc)

  -If the transaction is successfully both client and server( through payment number) receive transaction sms with all necessary details

  -Now the server phone which receive transaction SMSs wich is an android based with SMS synchronisation(gateway ) app send this SMS to server Odoo system for confirmation and data recording

  -Now Odoo system receive transaction SMS, authenticate the sender, extract all necessary informations and record them to appropriate fields in a Database ready for confirmation

  -To finish the payment process the client must enter the transaction Id/number he/she received through his mobile phone during transaction in a confirmation field on ecommerce site

  -When the payment is confirmed shipment is issued
