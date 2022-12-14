from datetime import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://gokul:12345@cluster0.mceoshi.mongodb.net/?retryWrites=true&w=majority")
db = cluster["laptop"]
users = db["users"]            # connection to MongoDb Database
orders = db["orders"]

# flask is to create web server & request is for send and get messages

# initialize app variable to flask application which takes the name of module as argument
app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")  # get text value
    number = request.form.get("From")  # get number value
    number = number.replace("whatsapp:", "")
    response = MessagingResponse()   # initializing MessagingResponse function
    user = users.find_one({"number": number})  # find user whose number is same to
    if not bool(user):
        response.message("Hi, thanks for contacting *The Unique Laptops*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To contact us \n 2️⃣ To order laptop \n 3️⃣ To know our working hours \n 4️⃣ "
                    "To get our address")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)

        if option == 1:
            response.message("You can contact us through phone or e-mail.\n\n*Phone*: 991234 56789 \n*E-mail* : contact@theuniquelaptop.io")
        elif option == 2:
            response.message("You have entered *ordering mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})  # The $set operator replaces the value of a field with the specified value.
            response.message("You can select one of the following laptop types to order: \n\n1️⃣ Notebook  \n2️⃣ Ultraportable \n3️⃣ Chromebook"
                            "\n4️⃣ MacBook \n5️⃣ Convertible (2-in-1) \n6️⃣ Netbook \n7️⃣ Tablet as a laptop \n0️⃣ Go Back")
            response.message("This are some pictures of our latest models👇.")
            msg1 = response.message("")
            msg2 = response.message("")
            msg3 = response.message("")
            msg4 = response.message("")
            msg5 = response.message("")
            msg1.media("https://www.apple.com/v/macbook-pro-14-and-16/b/images/overview/hero/intro__ewz1ro7xs14y_large.jpg")
            msg2.media("https://cdn.pocket-lint.com/r/s/970x/assets/images/151520-laptops-review-hands-on-apple-macbook-air-2020-initial-review-keyboard-dreams-become-a-reality-image1-dwyvdpnsl7.jpg")
            msg3.media("https://m.media-amazon.com/images/I/81fZmxBbQgL._AC_SL1500_.jpg")
            msg4.media("https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-13-9315-2in1/media-gallery/blue/tablet-xps-13-9315-blue-gallery-10.psd?fmt=pjpg&pscan=auto&scl=1&wid=4465&hei=2394&qlt=100,1&resMode=sharp2&size=4465,2394&chrss=full&imwidth=5000")
            msg5.media("https://lzd-img-global.slatic.net/g/p/8475993a5d85f746e17602ce60cde065.jpg_720x720q80.jpg_.webp")
        elif option == 3:
            response.message("We work everyday from *9 AM to 5 PM*.")
        elif option == 4:
            response.message("Our main headquarters is currently located at \n\n*No. 22-2, Jalan Kuchai Maju 19, Dinasti Sentral, Off Jalan Kuchai Lama, 58200, Kuala Lumpur, Wilayah Persekutuan, Malaysia, 58200 Kuala Lumpur*")
        else:
            response.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            response.message(
                "Hi, thanks for contacting *The Unique Laptops*.\nYou can choose from one of the options below: "
                "\n\n*Type*\n\n 1️⃣ To contact us \n 2️⃣ To order laptop \n 3️⃣ To know our working hours \n 4️⃣ "
                "To get our address")
        elif 1 <= option <= 9:
            laptops = ["Notebook", "Ultraportable", "Chromebook", "MacBook", "Convertible (2-in-1)", "Netbook", "Tablet as a laptop"]
            selected = laptops[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            response.message("Excellent choice 🤩")
            response.message("Please enter your address to confirm the order")
        else:
            response.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user ["item"]
        response.message("Thank you for shopping with us!")
        response.message(f"Your order for {selected} has been received and will be delivered within 2 hours")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        response.message(
            "Hi, thanks for contacting again.\nYou can choose from one of the options below: "
            "\n\n*Type*\n\n 1️⃣ To contact us \n 2️⃣ To order laptop \n 3️⃣ To know our working hours \n 4️⃣ "
            "To get our address")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"message": {"text": text, "date": datetime.now()}}})  # The $push operator appends a specified value to an array.
    return str(response)


if __name__ == "__main__":
    app.run()
