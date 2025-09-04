import requests
import pandas as pd
import streamlit as st

from io import StringIO

@st.cache_data
def load_madrid_events_data():
    """
    Load Madrid events data from the API and return as DataFrame
    """
    try:
        url = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.csv"
        
        # Make request to the API
        headers = {'Accept': 'text/csv'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Convert response content to DataFrame
        csv_content = StringIO(response.text)
        df = pd.read_csv(csv_content, sep=';')  # Madrid data often uses semicolon separator
        
        return df
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
   df = load_madrid_events_data()

   print(df.shape)
   print(df.columns)
