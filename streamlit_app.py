
import streamlit as st
import pandas as pd

from api_client import (
    upload_dataset,
    get_datasets,
    get_preview,
    get_dataset_info,
    clean_dataset,
    rename_columns,
    drop_columns,
    convert_datatype
)

st.set_page_config(
    page_title="Prep_AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Prep_AI")
st.subheader("Data Preprocessing and Visualization Platform")

st.write(
    "Upload, clean, transform, analyze and visualize "
    "your datasets in one place."
)

st.divider()

# Sidebar navigation
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Upload Dataset",
        "Manage Datasets",
        "Clean & Transform"
    ]
)


# Upload Dataset
if page == "Upload Dataset":

    st.header("📁 Upload Dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        if st.button("Upload Dataset"):

            try:
                result = upload_dataset(uploaded_file)

                st.success("Dataset uploaded successfully!")
                st.json(result)

            except Exception as e:
                st.error(f"Upload failed: {e}")


# Manage Datasets
elif page == "Manage Datasets":

    st.header("📚 Manage Datasets")

    try:
        datasets = get_datasets()

        if datasets:

            dataset_options = {
                f'{item["filename"]} ({item["dataset_id"][:8]})':
                item["dataset_id"]
                for item in datasets
            }

            selected_name = st.selectbox(
                "Select a dataset",
                list(dataset_options.keys())
            )

            dataset_id = dataset_options[selected_name]

            preview = get_preview(dataset_id)

            st.subheader("Dataset Preview")

            st.dataframe(
                pd.DataFrame(preview["preview"]),
                use_container_width=True
            )

            st.write("Total Rows:", preview["total_rows"])
            st.write("Total Columns:", preview["total_columns"])

            st.subheader("Dataset Information")

            info = get_dataset_info(dataset_id)
            st.json(info)

        else:
            st.info("No datasets uploaded yet.")

    except Exception as e:
        st.error(f"Unable to fetch datasets: {e}")


# Clean and Transform
elif page == "Clean & Transform":

    st.header("🧹 Clean & Transform Dataset")

    try:
        datasets = get_datasets()

        if not datasets:
            st.info("Please upload a dataset first.")

        else:

            dataset_options = {
                f'{item["filename"]} ({item["dataset_id"][:8]})':
                item["dataset_id"]
                for item in datasets
            }

            selected_name = st.selectbox(
                "Choose a dataset",
                list(dataset_options.keys())
            )

            dataset_id = dataset_options[selected_name]

            st.divider()

            st.subheader("1. Remove Missing Values and Duplicates")

            remove_missing = st.checkbox(
                "Remove rows containing missing values"
            )

            remove_duplicates = st.checkbox(
                "Remove duplicate rows"
            )

            if st.button("Clean Dataset"):

                if not remove_missing and not remove_duplicates:
                    st.warning("Select at least one cleaning operation.")

                else:
                    try:
                        result = clean_dataset(
                            dataset_id,
                            remove_missing,
                            remove_duplicates
                        )

                        st.success("Dataset cleaned successfully!")
                        st.json(result)

                    except Exception as e:
                        st.error(f"Cleaning failed: {e}")

            st.divider()

            st.subheader("2. Rename Columns")

            preview = get_preview(dataset_id)
            columns = preview["columns"]

            selected_column = st.selectbox(
                "Select column to rename",
                columns,
                key="rename_column"
            )

            new_column_name = st.text_input(
                "Enter new column name"
            )

            if st.button("Rename Column"):

                if not new_column_name.strip():
                    st.warning("Please enter a new column name.")

                elif new_column_name in columns:
                    st.warning("This column name already exists.")

                else:
                    try:
                        result = rename_columns(
                            dataset_id,
                            {selected_column: new_column_name}
                        )

                        st.success("Column renamed successfully!")
                        st.json(result)

                    except Exception as e:
                        st.error(f"Rename failed: {e}")

            st.divider()

            st.subheader("3. Drop Columns")

            columns_to_drop = st.multiselect(
                "Select columns to remove",
                columns
            )

            if st.button("Drop Selected Columns"):

                if not columns_to_drop:
                    st.warning("Please select at least one column.")

                else:
                    try:
                        result = drop_columns(
                            dataset_id,
                            columns_to_drop
                        )

                        st.success("Columns dropped successfully!")
                        st.json(result)

                    except Exception as e:
                        st.error(f"Drop failed: {e}")

            st.divider()

            st.subheader("4. Convert Data Type")

            column_to_convert = st.selectbox(
                "Select column",
                columns,
                key="convert_column"
            )

            new_type = st.selectbox(
                "Select new data type",
                ["int", "float", "str"]
            )

            if st.button("Convert Data Type"):

                try:
                    result = convert_datatype(
                        dataset_id,
                        column_to_convert,
                        new_type
                    )

                    st.success("Data type converted successfully!")
                    st.json(result)

                except Exception as e:
                    st.error(f"Conversion failed: {e}")

    except Exception as e:
        st.error(f"Unable to load cleaning tools: {e}")
