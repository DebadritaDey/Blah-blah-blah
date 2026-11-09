
import requests

# FastAPI backend URL
API_BASE_URL = "http://127.0.0.1:8000/api/v1/datasets"


# 1. GET ALL DATASETS
def get_datasets():
    response = requests.get(f"{API_BASE_URL}/")
    response.raise_for_status()
    return response.json()


# 2. UPLOAD DATASET
def upload_dataset(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/upload",
        files=files
    )

    response.raise_for_status()
    return response.json()


# 3. PREVIEW DATASET
def get_preview(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/preview"
    )

    response.raise_for_status()
    return response.json()


# 4. DATASET INFORMATION
def get_dataset_info(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/info"
    )

    response.raise_for_status()
    return response.json()


# 5. CLEAN DATASET
def clean_dataset(dataset_id, remove_missing_rows, remove_duplicates):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/clean",
        json={
            "remove_missing_rows": remove_missing_rows,
            "remove_duplicates": remove_duplicates
        }
    )

    response.raise_for_status()
    return response.json()


# 6. RENAME COLUMNS
def rename_columns(dataset_id, column_mapping):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/rename-columns",
        json={
            "column_mapping": column_mapping
        }
    )

    response.raise_for_status()
    return response.json()


# 7. DROP COLUMNS
def drop_columns(dataset_id, columns):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/drop-columns",
        json={
            "columns": columns
        }
    )

    response.raise_for_status()
    return response.json()


# 8. CONVERT DATA TYPE
def convert_datatype(dataset_id, column_name, new_type):
    response = requests.post(
        f"{API_BASE_URL}/{dataset_id}/convert-datatype",
        json={
            "column_name": column_name,
            "new_type": new_type
        }
    )

    response.raise_for_status()
    return response.json()


# 9. DESCRIPTIVE STATISTICS
def get_statistics(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/statistics"
    )

    response.raise_for_status()
    return response.json()


# 10. CORRELATION MATRIX
def get_correlation(dataset_id):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/correlation"
    )

    response.raise_for_status()
    return response.json()


# 11. HISTOGRAM
def get_histogram(dataset_id, column_name):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/histogram/{column_name}"
    )

    response.raise_for_status()
    return response.json()


# 12. BAR CHART
def get_bar_chart(dataset_id, column_name):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/bar-chart/{column_name}"
    )

    response.raise_for_status()
    return response.json()


# 13. SCATTER PLOT
def get_scatter_plot(dataset_id, x_column, y_column):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/scatter-plot",
        params={
            "x_column": x_column,
            "y_column": y_column
        }
    )

    response.raise_for_status()
    return response.json()


# 14. DOWNLOAD DATASET
def download_dataset(dataset_id, file_format="csv"):
    response = requests.get(
        f"{API_BASE_URL}/{dataset_id}/download",
        params={
            "file_format": file_format
        }
    )

    response.raise_for_status()
    return response.content



# HISTOGRAM

st.divider()
st.subheader("📊 Histogram")

if columns:
    histogram_column = st.selectbox(
        "Select a column for Histogram",
        columns,
        key="histogram_column"
    )

    if st.button("Generate Histogram"):

        try:
            histogram = get_histogram(
                dataset_id,
                histogram_column
            )

            histogram_df = pd.DataFrame(histogram["histogram"])

            fig = px.bar(
                histogram_df,
                x=histogram_df.columns[0],
                y=histogram_df.columns[1],
                title=f"Distribution of {histogram_column}"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Histogram failed: {e}")


# HISTOGRAM

st.divider()
st.subheader("📊 Histogram")

numeric_columns = []

try:
    preview_data = get_preview(dataset_id)
    data = preview_data.get(
        "preview",
        preview_data.get("data", [])
    )

    if data:
        dataset_df = pd.DataFrame(data)

        numeric_columns = dataset_df.select_dtypes(
            include="number"
        ).columns.tolist()

except Exception as e:
    st.error(f"Could not load numerical columns: {e}")


if numeric_columns:

    histogram_column = st.selectbox(
        "Select a numerical column",
        numeric_columns,
        key="histogram_column"
    )

    if st.button("Generate Histogram"):

        try:
            histogram = get_histogram(
                dataset_id,
                histogram_column
            )

            st.write("Histogram API Response:")
            st.json(histogram)

        except Exception as e:
            st.error(f"Histogram failed: {e}")

else:
    st.info("No numerical columns found in this dataset.")




# BAR CHART

st.divider()
st.subheader("📊 Bar Chart")

try:
    preview_data = get_preview(dataset_id)

    data = preview_data.get(
        "preview",
        preview_data.get("data", [])
    )

    dataset_df = pd.DataFrame(data)

    if not dataset_df.empty:

        categorical_columns = dataset_df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        if categorical_columns:

            bar_column = st.selectbox(
                "Select a categorical column",
                categorical_columns,
                key="bar_column"
            )

            if st.button("Generate Bar Chart"):

                counts = (
                    dataset_df[bar_column]
                    .value_counts()
                    .reset_index()
                )

                counts.columns = [bar_column, "Count"]

                fig = px.bar(
                    counts,
                    x=bar_column,
                    y="Count",
                    title=f"Count of {bar_column}",
                    text="Count"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        else:
            st.info("No categorical columns found.")

except Exception as e:
    st.error(f"Could not generate bar chart: {e}")






# SCATTER PLOT

st.divider()
st.subheader("🔵 Scatter Plot")

try:
    preview_data = get_preview(dataset_id)

    data = preview_data.get(
        "preview",
        preview_data.get("data", [])
    )

    dataset_df = pd.DataFrame(data)

    numeric_columns = dataset_df.select_dtypes(
        include="number"
    ).columns.tolist()

    if len(numeric_columns) >= 2:

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox(
                "Select X-axis",
                numeric_columns,
                key="scatter_x"
            )

        with col2:
            y_options = [
                col for col in numeric_columns
                if col != x_column
            ]

            y_column = st.selectbox(
                "Select Y-axis",
                y_options,
                key="scatter_y"
            )

        if st.button("Generate Scatter Plot"):

            fig = px.scatter(
                dataset_df,
                x=x_column,
                y=y_column,
                title=f"{y_column} vs {x_column}",
                color_discrete_sequence=["#636EFA"]
            )

            fig.update_layout(
                xaxis_title=x_column,
                yaxis_title=y_column
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info(
            "At least two numerical columns are required "
            "for a scatter plot."
        )

except Exception as e:
    st.error(f"Could not generate scatter plot: {e}")


# DOWNLOAD DATASET

elif page == "Download Dataset":

    st.header("📥 Download Dataset")

    datasets = load_datasets()
    selected = select_dataset(datasets)

    if selected:

        dataset_id = selected["dataset_id"]

        st.write("Selected file:", selected["filename"])

        file_format = st.selectbox(
            "Choose Download Format",
            ["csv", "xlsx"]
        )

        if st.button("Download Dataset"):

            try:
                file_content = download_dataset(
                    dataset_id,
                    file_format
                )

                filename = (
                    selected["filename"].rsplit(".", 1)[0]
                    + "." + file_format
                )

                st.download_button(
                    label="Click Here to Save File",
                    data=file_content,
                    file_name=filename,
                    mime=(
                        "text/csv"
                        if file_format == "csv"
                        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                )

            except Exception as e:
                st.error(f"Download failed: {e}")
with col1:
            st.metric("Total Rows", info.get("row_count", 0))

        with col2:
            st.metric("Total Columns", info.get("column_count", 0))

        with col3:
            st.metric(
                "Missing Values",
                sum(info.get("missing_values", {}).values())
            )

        st.write("**Dataset ID:**", info.get("dataset_id", dataset_id))
