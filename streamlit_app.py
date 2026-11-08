
import streamlit as st
import pandas as pd

from api_client import (
    get_datasets,
    upload_dataset,
    get_preview,
    get_dataset_info,
    clean_dataset,
    rename_columns,
    drop_columns,
    convert_datatype,
    get_statistics,
    get_correlation
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Prep_AI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Prep_AI")
st.caption("Data Preprocessing and Exploratory Data Analysis")


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def load_datasets():
    try:
        return get_datasets()
    except Exception as e:
        st.error(f"Could not load datasets: {e}")
        return []


def select_dataset(datasets):
    if not datasets:
        st.warning("Please upload a dataset first.")
        return None

    selected = st.selectbox(
        "Select Dataset",
        datasets,
        format_func=lambda x: x["filename"]
    )

    return selected


def show_result(result):
    st.success(result.get("message", "Operation completed successfully!"))


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Upload Dataset",
        "Manage Datasets",
        "Clean & Transform",
        "EDA Dashboard"
    ]
)


# --------------------------------------------------
# PAGE 1: UPLOAD DATASET
# --------------------------------------------------

if page == "Upload Dataset":

    st.header("Upload Dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

    if st.button("Upload Dataset"):

        if uploaded_file is None:
            st.warning("Please select a file first.")

        else:
            try:
                result = upload_dataset(uploaded_file)

                st.success("Dataset uploaded successfully!")

                st.write("**Filename:**", result["filename"])
                st.write("**Rows:**", result["row_count"])
                st.write("**Columns:**", result["column_count"])

            except Exception as e:
                st.error(f"Upload failed: {e}")


# --------------------------------------------------
# PAGE 2: MANAGE DATASETS
# --------------------------------------------------

elif page == "Manage Datasets":

    st.header("Manage Datasets")

    datasets = load_datasets()
    selected = select_dataset(datasets)

    if selected:

        dataset_id = selected["dataset_id"]

        st.subheader("Dataset Overview")

        col1, col2 = st.columns(2)

        col1.metric("Rows", selected["row_count"])
        col2.metric("Columns", selected["column_count"])

        if st.button("Preview Dataset"):

            try:
                preview = get_preview(dataset_id)

                st.subheader("Dataset Preview")

                data = preview.get(
                    "preview",
                    preview.get("data", [])
                )

                st.dataframe(
                    pd.DataFrame(data),
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Preview failed: {e}")

        if st.button("View Dataset Information"):

            try:
                info = get_dataset_info(dataset_id)

                st.subheader("Dataset Information")
                st.json(info)

            except Exception as e:
                st.error(f"Could not load information: {e}")


# --------------------------------------------------
# PAGE 3: CLEAN AND TRANSFORM
# --------------------------------------------------

elif page == "Clean & Transform":

    st.header("Clean & Transform Dataset")

    datasets = load_datasets()
    selected = select_dataset(datasets)

    if selected:

        dataset_id = selected["dataset_id"]

        try:
            preview = get_preview(dataset_id)
            columns = preview.get("columns", [])

            if not columns:
                data = preview.get("preview", preview.get("data", []))
                if data:
                    columns = list(data[0].keys())

        except Exception as e:
            st.error(f"Could not load columns: {e}")
            columns = []

        operation = st.selectbox(
            "Choose an Operation",
            [
                "Remove Missing Values",
                "Remove Duplicates",
                "Rename Columns",
                "Drop Columns",
                "Convert Data Type"
            ]
        )

        st.divider()

        # REMOVE MISSING VALUES

        if operation == "Remove Missing Values":

            st.write("Remove rows containing missing values.")

            if st.button("Remove Missing Rows"):

                try:
                    result = clean_dataset(
                        dataset_id,
                        True,
                        False
                    )
                    show_result(result)

                except Exception as e:
                    st.error(f"Operation failed: {e}")

        # REMOVE DUPLICATES

        elif operation == "Remove Duplicates":

            st.write("Remove duplicate rows from the dataset.")

            if st.button("Remove Duplicate Rows"):

                try:
                    result = clean_dataset(
                        dataset_id,
                        False,
                        True
                    )
                    show_result(result)

                except Exception as e:
                    st.error(f"Operation failed: {e}")

        # RENAME COLUMNS

        elif operation == "Rename Columns":

            if columns:

                old_name = st.selectbox(
                    "Select Column",
                    columns
                )

                new_name = st.text_input(
                    "Enter New Column Name"
                )

                if st.button("Rename Column"):

                    if not new_name.strip():
                        st.warning("Enter a new column name.")

                    else:
                        try:
                            result = rename_columns(
                                dataset_id,
                                {old_name: new_name}
                            )
                            show_result(result)

                        except Exception as e:
                            st.error(f"Rename failed: {e}")

            else:
                st.info("No columns available.")

        # DROP COLUMNS

        elif operation == "Drop Columns":

            if columns:

                selected_columns = st.multiselect(
                    "Select Columns to Drop",
                    columns
                )

                if st.button("Drop Selected Columns"):

                    if not selected_columns:
                        st.warning("Select at least one column.")

                    else:
                        try:
                            result = drop_columns(
                                dataset_id,
                                selected_columns
                            )
                            show_result(result)

                        except Exception as e:
                            st.error(f"Drop failed: {e}")

            else:
                st.info("No columns available.")

        # CONVERT DATA TYPE

        elif operation == "Convert Data Type":

            if columns:

                column_name = st.selectbox(
                    "Select Column",
                    columns
                )

                new_type = st.selectbox(
                    "Choose New Data Type",
                    ["int", "float", "str"]
                )

                if st.button("Convert Data Type"):

                    try:
                        result = convert_datatype(
                            dataset_id,
                            column_name,
                            new_type
                        )
                        show_result(result)

                    except Exception as e:
                        st.error(f"Conversion failed: {e}")

            else:
                st.info("No columns available.")


# --------------------------------------------------
# PAGE 4: EDA DASHBOARD
# --------------------------------------------------

elif page == "EDA Dashboard":

    st.header("📈 Exploratory Data Analysis")

    st.write(
        "Explore descriptive statistics and relationships "
        "between numerical variables."
    )

    datasets = load_datasets()
    selected = select_dataset(datasets)

    if selected:

        dataset_id = selected["dataset_id"]

        # DESCRIPTIVE STATISTICS

        st.subheader("Descriptive Statistics")

        if st.button("Generate Statistics"):

            try:
                statistics = get_statistics(dataset_id)
                st.write(statistics)

            except Exception as e:
                st.error(f"Could not generate statistics: {e}")

        st.divider()

        # CORRELATION MATRIX

        st.subheader("Correlation Analysis")

        if st.button("Generate Correlation Matrix"):

            try:
                correlation = get_correlation(dataset_id)
                st.write(correlation)

            except Exception as e:
                st.error(f"Could not generate correlation: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.caption("Prep_AI | Data Analysis Platform")
