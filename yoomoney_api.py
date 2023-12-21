from yoomoney import Authorize
from yoomoney import Client
from yoomoney import Quickpay

TOKEN = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'

def authorize():
    Authorize(
        client_id="BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
        redirect_uri="https://t.me/lifestyle_tracker_bot",
        scope=["account-info",
                "operation-history",
                "operation-details",
                "incoming-transfers",
                "payment-p2p",
                "payment-shop",
                ]
        )

def print_account_info():
    client = Client(TOKEN)
    user = client.account_info()
    print("Account number:", user.account)
    print("Account balance:", user.balance)
    print("Account currency code in ISO 4217 format:", user.currency)
    print("Account status:", user.account_status)
    print("Account type:", user.account_type)
    print("Extended balance information:")
    for pair in vars(user.balance_details):
        print("\t-->", pair, ":", vars(user.balance_details).get(pair))
    print("Information about linked bank cards:")
    cards = user.cards_linked
    if len(cards) != 0:
        for card in cards:
            print(card.pan_fragment, " - ", card.type)
    else:
        print("No card is linked to the account")

def generate_payment_url(sum, label) -> str:
    quickpay = Quickpay(
            receiver="4100117889201888",
            quickpay_form="shop",
            targets="LifeStyle Tracker - покупка подписки",
            paymentType="SB",
            sum=sum,
            label= label,
            comment="LifeStyle Tracker - покупка подписки",
            successURL='https://t.me/lifestyle_tracker_bot'
            )
    return quickpay.redirected_url

def get_is_bill_paid(bill_label):
    client = Client(TOKEN)
    history = client.operation_history(label=bill_label)
    for operation in history.operations:
        return operation.status == 'success'

if __name__ == '__main__':
    #print(generate_payment_form(2, 'Molot369-123'))
    print(get_is_bill_paid('Molot369-123'))