# Import Python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake (assuming st.connection is correctly defined)
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)

    # Process ingredients selection
    if ingredients_list:
        ingredients_string = ' '.join(ingredients_list)  # Join selected ingredients into a single string
        for fruit_chosen in ingredients_list:
            try:
                # Format fruit name for API
                fruit_api_name = fruit_chosen.lower().replace(' ', '-')
                fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_api_name}")
                fruityvice_response.raise_for_status()

                # Parse and display fruit nutrition info
                fruit_info = fruityvice_response.json()
                st.subheader(f"{fruit_chosen} Nutrition Information")
                st.dataframe(data=[fruit_info], use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.warning(f"Failed to fetch details for {fruit_chosen}: {str(e)}")

        # Submit button for placing order
        time_to_insert = st.button("Submit Order")
        if time_to_insert:
            if not name_on_order.strip():
                st.error("Please enter a name for your smoothie.")
            else:
                try:
                    session.table("smoothies.public.orders").insert([
                        {"INGREDIENTS": ingredients_string, "NAME_ON_ORDER": name_on_order}
                    ])
                    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
                except Exception as e:
                    st.error(f"Failed to submit your order: {str(e)}")


except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")

# Display a link
st.write("https://github.com/appuv")
