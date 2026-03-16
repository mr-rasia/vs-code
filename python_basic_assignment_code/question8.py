import json
import csv

DISCOUNT_RATE = 0.10
SHIPPING_PER_ITEM = 5


def process_orders():

    # Read JSON file
    with open("sales.json", "r") as file:
        data = json.load(file)

    orders = data.get("orders", [])

    processed_data = []

    for order in orders:

        order_id = order.get("order_id", "N/A")

        customer = order.get("customer", {})
        customer_name = customer.get("name", "Unknown")

        address = order.get("shipping_address", "Unknown")
        country_code = "US"  # since address is US

        items = order.get("items", [])

        for item in items:

            product_name = item.get("name", "Unknown")
            price = item.get("price", 0)
            quantity = item.get("quantity", 0)

            total_value = price * quantity

            # Discount logic
            if total_value > 100:
                discount = total_value * DISCOUNT_RATE
            else:
                discount = 0

            shipping_cost = quantity * SHIPPING_PER_ITEM

            final_total = total_value - discount + shipping_cost

            processed_data.append([
                order_id,
                customer_name,
                product_name,
                price,
                quantity,
                round(total_value, 2),
                round(discount, 2),
                shipping_cost,
                round(final_total, 2),
                address,
                country_code
            ])

    # Sort by final total
    processed_data.sort(key=lambda x: x[8], reverse=True)

    # CSV Header
    header = [
        "Order ID",
        "Customer Name",
        "Product Name",
        "Product Price",
        "Quantity Purchased",
        "Total Value",
        "Discount",
        "Shipping Cost",
        "Final Total",
        "Shipping Address",
        "Country Code"
    ]

    # Write CSV
    with open("output.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(header)
        writer.writerows(processed_data)

    print("CSV file generated: output.csv")


process_orders()