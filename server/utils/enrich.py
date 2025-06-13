import json
import logging
from typing import Union
import pandas as pd
import warnings

logger = logging.getLogger("lida")

system_prompt = """
You are an experienced data analyst that can annotate datasets. Your instructions are as follows:
i) ALWAYS generate the name of the dataset and the dataset_description
ii) ALWAYS generate a field description.
iii.) ALWAYS generate a semantic_type (a single word) for each field given its values e.g. company, city, number, supplier, location, gender, longitude, latitude, url, ip address, zip code, email, etc
You must return an updated JSON dictionary without any preamble or explanation.
You MUST NOT add ```json ``` to the beginning and end.
"""

def read_dataframe(file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
    """Read a dataframe from various file formats"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path, encoding=encoding)
    elif file_path.endswith('.parquet'):
        return pd.read_parquet(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path, orient="records", lines=True)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

class Summarizer():
    def __init__(self) -> None:
        self.summary = None

    def check_type(self, dtype: str, value):
        """Cast value to right type to ensure it is JSON serializable"""
        if "float" in str(dtype):
            return float(value)
        elif "int" in str(dtype):
            return int(value)
        else:
            return value

    def get_column_properties(self, df: pd.DataFrame, n_samples: int = 3) -> list[dict]:
        """Get properties of each column in a pandas DataFrame"""
        properties_list = []
        for column in df.columns:
            dtype = df[column].dtype
            properties = {}
            if dtype in [int, float, complex]:
                properties["dtype"] = "number"
                properties["std"] = self.check_type(dtype, df[column].std())
                properties["min"] = self.check_type(dtype, df[column].min())
                properties["max"] = self.check_type(dtype, df[column].max())

            elif dtype is bool or str(dtype) == 'bool':
                properties["dtype"] = "boolean"
            elif dtype is object or str(dtype) == 'object':
                # Check if the string column can be cast to a valid datetime
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        pd.to_datetime(df[column], errors='raise')
                        properties["dtype"] = "date"
                except ValueError:
                    # Check if the string column has a limited number of values
                    if df[column].nunique() / len(df[column]) < 0.5:
                        properties["dtype"] = "category"
                    else:
                        properties["dtype"] = "string"
            elif pd.api.types.is_categorical_dtype(df[column]):
                properties["dtype"] = "category"
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                properties["dtype"] = "date"
            else:
                properties["dtype"] = str(dtype)

            # add min max if dtype is date
            if properties["dtype"] == "date":
                try:
                    properties["min"] = df[column].min()
                    properties["max"] = df[column].max()
                except TypeError:
                    cast_date_col = pd.to_datetime(df[column], errors='coerce')
                    properties["min"] = cast_date_col.min()
                    properties["max"] = cast_date_col.max()
            # Add additional properties to the output dictionary
            nunique = df[column].nunique()
            if "samples" not in properties:
                non_null_values = df[column][df[column].notnull()].unique()
                n_samples = min(n_samples, len(non_null_values))
                samples = pd.Series(non_null_values).sample(
                    n_samples, random_state=42).tolist()
                properties["samples"] = samples
            properties["num_unique_values"] = nunique
            properties["semantic_type"] = ""
            properties["description"] = ""
            properties_list.append(
                {"column": column, "properties": properties})

        return properties_list

    def enrich(self, base_summary: dict, text_gen) -> dict:
        """Enrich the data summary with descriptions"""
        logger.info("Enriching the data summary with descriptions")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"""
        Annotate the dictionary below. Only return a JSON object.
        {base_summary}
        """},
        ]
        prompt = "\n\n".join(msg["content"] for msg in messages)
        prompts = [prompt]
        response = text_gen.invoke(prompts)

        # extract the generated text from LLMResult

        # attach column names for reference
        # data_summary["field_names"] = data_simmary.tolist()

        # return the enriched summary dict
        return json.dumps(response.content)

    def summarize(
            self, data: Union[pd.DataFrame, str],
            text_gen, file_name="", n_samples: int = 3,
            summary_method: str = "default", encoding: str = 'utf-8') -> dict:
        """Summarize data from a pandas DataFrame or a file location"""

        # if data is a file path, read it into a pandas DataFrame, set file_name to the file name
        if isinstance(data, str):
            file_name = data.split("/")[-1]
            # modified to include encoding
            data = read_dataframe(data, encoding=encoding)
        data_properties = self.get_column_properties(data, n_samples)

        # default single stage summary construction
        base_summary = {
            "name": file_name,
            "file_name": file_name,
            "dataset_description": "",
            "fields": data_properties,
        }

        data_summary = base_summary

        if summary_method == "llm":
            # two stage summarization with llm enrichment
            data_summary = self.enrich(
                base_summary,
                text_gen=text_gen,
                )
        elif summary_method == "columns":
            # no enrichment, only column names
            data_summary = {
                "name": file_name,
                "file_name": file_name,
                "dataset_description": ""
            }

        # data_summary["field_names"] = data.columns.tolist()
        # data_summary["file_name"] = file_name

        return data_summary