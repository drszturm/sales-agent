# pip3 install langchain_openai
# python3 deepseek_langchain.py
import pandas as pd
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from config import settings

# Read entire XLSX file


class DeepSeekLCService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.llm = create_agent(
            checkpointer=InMemorySaver(),
            model="deepseek-chat",  # intalled model="claude-sonnet-4-5-20250929",
            tools=[load_products, set_customer_contact, get_actual_phone_number],
            system_prompt="You are a helpful supermarket salesman.You are a a supermarket salesman that want be helpful. Be concise and accurate."
            "The supermarket is located in Brazil and sells groceries and household items."
            "load files and use it to answer customer questions about products and prices."
            "ask custommer name an use tool set_customer_contact to store it with the telephone number provided by the tool get_actual_phone_number."
            "if the customer ask for product list, load the product list use the tool load_products and provide options"
            "The supermarket name is Bom preço Supermercados."
            "It is located at 9 de Julho Avenue, 1234, São Paulo, SP, Brazil."
            "Do not say you are an AI model, always pretend to be a human supermarket salesman."
            "DO not say the product list with prices befeore the customer ask for it."
            "start the conversation always with good morning, good afternoon or good night based on current time. gmt -3 timezone."
            " give options for products and values, calculate total when asked for,"
            " answer in portuguese from brazil. when the question is not related to supermarket,"
            " answer that you are a supermarket salesman and can only help with supermarket related questions."
            "when providing product options, always include prices and quantities."
            " when the person finish the purchase, provide a summary of the items bought with total value."
            " and than ask payment method 1 for pix, 2 for credit card , 3 for debit card or 4 for cash or 5 in person payment."
            " ask the address for delivery and if the person want delivery."
            " if payment method is pix, generate a fake pix code."
            "the prices are the same as a supermarket in brazil. as https://www.google.com/aclk?sa=L&pf=1&ai=DChsSEwiQgt635d6QAxWaU0gAHaK-EBwYACICCAEQARoCY2U&co=1&ase=2&gclid=Cj0KCQiAq7HIBhDoARIsAOATDxAdGrpqvi2YryVg68hujRJIrTHq5EOzpzvHn6d2maMkUaE7OAb5-QMaAv8DEALw_wcB&cid=CAAS9gHkaOkONc8eLUmAzvNBQ_myGZUaM6HPAuwtdwoMT0iF54fY0rs1sDfJj6-OtpzwX8XARn2UeeJ2zdvzk8z1cibzpum6C_ngv8cB_4XswWWm6w_EaUzi2DbPb_vYFFmnbPiCzbCZMXkTZFspONvsvpCWjYJhZV4XEOwZcEaPpMX8YoQbiLT47eIkK66Q-necjv6l-zBDosiRD4QrPEFMWBkGt97myvETA_DWPEL1O1ABEHfLsTbvPaAZL9xC2-IJ6TuZIINwrL6rrwVKMSwOKx_YrrniNBzqo_uEI6ILPfthhMInK91EvMNgo0aPm2Lccy19FnXZEe8&cce=2&category=acrcp_v1_32&sig=AOD64_3JkmjAPtiN1JNhUZ8NndgrB-mHng&q&nis=4&adurl=https://mercado.carrefour.com.br"
            " always ask how can you help the customer.",
        )

    def chat_completion(
        self, messages, max_tokens=2048, temperature=0.7, stream=False, prompt=""
    ):
        print("Invoking DeepSeek LLM via LangChain...")
        print("Messages:", messages)
        response = self.llm.invoke(
            {
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in messages
                ]
            },
            {"configurable": {"thread_id": "1"}},
        )
        print(response)
        print("Response content:", response["messages"])
        return response["messages"][-1]


def load_products():
    """
    Load the product list from the local Excel file 'produtos.xlsx'.

    This function return the  product list for the supermarket salesman.

    Returns:
        pandas.DataFrame: DataFrame containing product data loaded from
        'produtos.xlsx'.

    Raises:
        FileNotFoundError: If 'produtos.xlsx' does not exist in the current
            working directory.
        ValueError, XLRDError, or other pandas-related exceptions raised by
            pandas.read_excel when the file cannot be parsed.

    Notes:
        - The path to the Excel file is hard-coded; change the implementation
          if you need to load from a different location or allow caller-specified paths.
        - The caller is responsible for importing pandas as pd before calling
          this function (or the module should import it).
        - Consider adding validation of expected columns after loading if the
          consumer relies on specific fields.
    """
    df = pd.read_excel("produtos.xlsx")
    return df


def set_customer_contact(name: str, cellphone: str) -> str:
    """
    Store the customer's name for personalized interactions.

    This function simulates storing the customer's name, which can be used
    later in conversations to enhance user experience.

    Args:
        name (str): The name of the customer to store.

    Returns:
        str: Confirmation message indicating the name has been stored.
    """
    # In a real implementation, this could store the name in a database
    # or session context. Here, we simply return a confirmation message.
    return f"Customer name '{name}' has been stored."


def get_actual_phone_number() -> str:
    """
    Retrieve the actual phone number of the customer.

    This function simulates retrieving the customer's phone number,
    which can be used for contact or identification purposes.

    Returns:
        str: The customer's phone number.
    """
    # In a real implementation, this could retrieve the phone number from
    # session context or request metadata. Here, we return a placeholder.
    return "+55 11 91234-5678"


def get_customer_by_phone_number(phone_number: str) -> str | None:
    """
    Retrieve the customer's name based on their phone number.

    This function simulates looking up a customer's name using their
    phone number, which can be useful for personalized interactions.

    Args:
        phone_number (str): The phone number of the customer.
    Returns:
        str: The name of the customer associated with the phone number.
        None: If no customer is found for the given phone number.
    """

    # In a real implementation, this could query a database.
    # Here, we return a placeholder name.
    return "Customer Name"


deepseek_lc_service = DeepSeekLCService()
