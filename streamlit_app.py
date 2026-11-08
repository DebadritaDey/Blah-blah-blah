
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
st.subheader("Data Preprocessing and Visualization Platform")

st.write(
    "Upload, clean, transform, analyze and visualize "
    "your datasets in one place."
)

st.divider()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def load_datasets():

    datasets = get_datasets()

    if not datasets:
        return {}

    return {
        f'{item["filename"]} ({item["dataset_id"][:8]})':
        item["dataset_id"]
        for item in datasets
    }


def show_operation_result(operation):

    st.success(f"{operation} completed successfully!")

    st.info(
        "A new processed dataset has been created. "
        "Your original dataset remains unchanged."
    )


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("Prep_AI")

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
# UPLOAD DATASET
# --------------------------------------------------

if page == "Upload Dataset":

    st.header("📁 Upload Dataset")

    st.write("Upload a CSV or Excel file.")

    uploaded_file = st.file_uploader(
        "Choose a dataset",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        st.write("Selected file:", uploaded_file.name)

        if st.button("Upload Dataset", type="primary"):

            try:

                with st.spinner("Uploading dataset..."):

                    result = upload_dataset(uploaded_file)

                st.success("Dataset uploaded successfully!")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Rows", result["row_count"])

                with col2:
                    st.metric("Total Columns", result["column_count"])

                st.write("Filename:", result["filename"])

            except Exception as e:

                st.error(f"Upload failed: {e}")


# --------------------------------------------------
# MANAGE DATASETS
# --------------------------------------------------

elif page == "Manage Datasets":

    st.header("📚 Manage Datasets")

    try:

        dataset_options = load_datasets()

        if not dataset_options:

            st.info("No datasets uploaded yet.")

        else:

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

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Rows", preview["total_rows"])

            with col2:
                st.metric("Total Columns", preview["total_columns"])

            st.divider()

            st.subheader("Dataset Information")

            info = get_dataset_info(dataset_id)

            st.json(info)

    except Exception as e:

        st.error(f"Unable to fetch datasets: {e}")


# --------------------------------------------------
# CLEAN AND TRANSFORM
# --------------------------------------------------

elif page == "Clean & Transform":

    st.header("🧹 Clean & Transform Dataset")

    try:

        dataset_options = load_datasets()

        if not dataset_options:

            st.info("Please upload a dataset first.")

        else:

            selected_name = st.selectbox(
                "Choose a dataset",
                list(dataset_options.keys())
            )

            dataset_id = dataset_options[selected_name]

            preview = get_preview(dataset_id)
            columns = preview["columns"]

            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "Clean Data",
                    "Rename Columns",
                    "Drop Columns",
                    "Convert Data Type"
                ]
            )

            # Clean data
            with tab1:

                st.subheader("Remove unwanted data")

                remove_missing = st.checkbox(
                    "Remove rows containing missing values"
                )

                remove_duplicates = st.checkbox(
                    "Remove duplicate rows"
                )

                if st.button("Clean Dataset", type="primary"):

                    if not remove_missing and not remove_duplicates:

                        st.warning("Select at least one operation.")

                    else:

                        try:

                            result = clean_dataset(
                                dataset_id,
                                remove_missing,
                                remove_duplicates
                            )

                            show_operation_result("Data cleaning")

                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric(
                                    "Rows Before",
                                    preview["total_rows"]
                                )

                            with col2:
                                st.metric(
                                    "Columns",
                                    preview["total_columns"]
                                )

                        except Exception as e:

                            st.error(f"Cleaning failed: {e}")

            # Rename columns
            with tab2:

                st.subheader("Rename columns")

                selected_column = st.selectbox(
                    "Select column",
                    columns,
                    key="rename_column"
                )

                new_column_name = st.text_input(
                    "Enter new column name"
                )

                if st.button("Rename Column", type="primary"):

                    if not new_column_name.strip():

                        st.warning("Enter a new column name.")

                    elif new_column_name in columns:

                        st.warning("Column name already exists.")

                    else:

                        try:

                            result = rename_columns(
                                dataset_id,
                                {selected_column: new_column_name.strip()}
                            )

                            show_operation_result("Column renaming")

                        except Exception as e:

                            st.error(f"Rename failed: {e}")

            # Drop columns
            with tab3:

                st.subheader("Remove unnecessary columns")

                columns_to_drop = st.multiselect(
                    "Select columns to remove",
                    columns
                )

                if st.button("Drop Selected Columns", type="primary"):

                    if not columns_to_drop:

                        st.warning("Select at least one column.")

                    elif len(columns_to_drop) == len(columns):

                        st.warning("You cannot remove all columns.")

                    else:

                        try:

                            result = drop_columns(
                                dataset_id,
                                columns_to_drop
                            )

                            st.success("Columns removed successfully!")

                            col1, col2 = st.columns(2)

                            with col1:
                                st.metric(
                                    "Columns Removed",
                                    len(result["removed_columns"])
                                )

                            with col2:
                                st.metric(
                                    "Columns Remaining",
                                    len(result["remaining_columns"])
                                )

                            st.write(
                                "Removed:",
                                ", ".join(result["removed_columns"])
                            )

                            st.write(
                                "Remaining:",
                                ", ".join(result["remaining_columns"])
                            )

                            st.info(
                                "Your original dataset remains unchanged."
                            )

                        except Exception as e:

                            st.error(f"Drop failed: {e}")

            # Convert datatype
            with tab4:

                st.subheader("Convert column data type")

                column_to_convert = st.selectbox(
                    "Select column",
                    columns,
                    key="convert_column"
                )

                new_type = st.selectbox(
                    "Select new data type",
                    ["int", "float", "str"]
                )

                if st.button("Convert Data Type", type="primary"):

                    try:

                        result = convert_datatype(
                            dataset_id,
                            column_to_convert,
                            new_type
                        )

                        show_operation_result("Data type conversion")

                    except Exception as e:

                        st.error(f"Conversion failed: {e}")


# --------------------------------------------------
# EDA DASHBOARD
# --------------------------------------------------

elif page == "EDA Dashboard":

    st.header("📈 Exploratory Data Analysis")

    st.write(
        "Explore descriptive statistics, missing values "
        "and relationships between numerical variables."
    )

    try:

        dataset_options = load_datasets()

        if not dataset_options:

            st.info("Please upload a dataset first.")

        else:

            selected_name = st.selectbox(
                "Select dataset for analysis",
                list(dataset_options.keys())
            )

            dataset_id = dataset_options[selected_name]

            # Dataset information
            preview = get_preview(dataset_id)
            info = get_dataset_info(dataset_id)

            st.divider()

            # Overview
            st.subheader("Dataset Overview")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Rows", preview["total_rows"])

            with col2:
                st.metric("Total Columns", preview["total_columns"])

            # Descriptive statistics
            st.divider()

            st.subheader("1. Descriptive Statistics")

            statistics = get_statistics(dataset_id)

            if statistics:

                stats_df = pd.DataFrame(statistics)

                st.dataframe(
                    stats_df,
                    use_container_width=True
                )

            else:

                st.info("No numerical columns available for statistics.")

            # Missing value analysis
            st.divider()

            st.subheader("2. Missing Value Analysis")

            if "missing_values" in info:

                missing_df = pd.DataFrame(
                    list(info["missing_values"].items()),
                    columns=["Column", "Missing Values"]
                )

                st.dataframe(
                    missing_df,
                    use_container_width=True
                )

                total_missing = missing_df["Missing Values"].sum()

                st.metric("Total Missing Values", int(total_missing))

            else:

                st.info("Missing value information is unavailable.")

            # Correlation analysis
            st.divider()

            st.subheader("3. Correlation Analysis")

            correlation = get_correlation(dataset_id)

            if correlation:

                correlation_df = pd.DataFrame(correlation)

                st.dataframe(
                    correlation_df.style.background_gradient(
                        cmap="coolwarm",
                        axis=None
                    ).format("{:.2f}"),
                    use_container_width=True
                )

            else:

                st.info(
                    "Not enough numerical columns for correlation analysis."
                )

    except Exception as e:

        st.error(f"EDA analysis failed: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Prep_AI | Data Preprocessing & Visualization Platform"
)
