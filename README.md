# Concepto Interior ([check it here](https://concepto-interior.herokuapp.com/))

Concepto Interior is a furniture shop based in Mexico. The ambition is to start delivring prodcuts all over the repubblic of Mexico using this website.

## UX

This website is designed for 2 different users : the customer and the seller.

### User stories

- Customer

1. I want to see only products I am interested in. I want to be able to filter and order them so that I can find the product I really need.
2. I want to be given the possibility to choose the payment method.
3. I want to be informed if my items are shipped and I want to receive all relevant information about the shipping.
4. I want to be informed before I buy a product if that is not deliverable to my place.
5. I want to have all my orders and preorders visible at a glance.
6. I want to be updated about any action taken on my order by email .

- Seller

1. I want to have an idea of how business is going and how much available inventory I have at a glance.
2. I want to offer to the user the possibility to pay by PayPal. It is more convenient for me, and I am ready to offer a discount on the grand total.
3. I want to set different delivery rates depending on the delivery destination
4. I want the user to be automatically informed by email when I take any action on an order.

## Features

### Existing Features

- Management: allows sellers to keep track and modify inventory, orders and preorders. Amending orders / preorders allows seller to send automatic emails to customers and keep them updated of order/preorder/shipment status. The seller can also set a minimum amount for free delivery orders. 
- Profile: allows users to amend delivery information and keep track of orders and preorders
- Products:allows user to see the products, filter and order them
- Checkout:allows user get a PayPal invoice or to pay directly (Stripe). The Stripe payment is done using the support of a web hooker. This ensures that orders are always correctly registered in the server. In case the payment was processed but order was not processed by mistake , webhooker will create an order.

## Technologies Used

- [JQuery](https://jquery.com)
    - The project uses **JQuery** to simplify DOM manipulation.
- [Django3](https://docs.djangoproject.com/)
    - The project uses **Django 3** as framework to achieve rapid development and clean, pragmatic design.
- [Bootstrap4](https://getbootstrap.com/)
    - The project uses **Bootstrap 4** to achieve a responsive, mobile-first site.
- [Python 3](https://www.python.org//)
    - The project uses **Python3** for back-end development.
- [Stripe](https://stripe.com/)
    - The project uses **Stripe** for onnline payment processing.
- [Heroku](https://heroku.com/)
    - The project uses **Heroku** as deployment evoiroment.
- [AWS Simple Cloud Storage (S3)](https://aws.amazon.com/s3/)
    - The project uses **S3** to store media and static files during deployment.
- [PostgreSQL](https://www.postgresql.org/)
    - The project uses **PostgreSQ** as object-relational database system during deployment.
- [Gmail](https://mail.google.com/)
    - The project uses **Gmail** SMTP server to manage email sending during deployment.
- [Git](https://git-scm.com//)
    - The project uses **Git** as version control system.


## Want to see how it looks like ?

- The webiste is temporary deployed on [Heroku](https://concepto-interior.herokuapp.com/)


