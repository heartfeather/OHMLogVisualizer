import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("OHM Log Visualizer")

def initSessionStateVariables():
  if 'dataframe' not in st.session_state:
    st.session_state.dataframe = None
  if 'basenames' not in st.session_state:
    st.session_state.basenames = None

def replaceDuplicates(n):
  hash = {}

  for i in range(len(n)):
    if n[i] not in hash:
      hash[n[i]] = 1
    else:
      count = hash[n[i]]
      hash[n[i]] += 1
      n[i] += '_' + str(count)

def fileUploaded(f):
  matrix = pd.read_csv(f, header=None).to_numpy()
  st.session_state.basenames = matrix[0][1:]
  replaceDuplicates(matrix[1])
  st.session_state.dataframe = pd.DataFrame(data=matrix[2:], columns=matrix[1])

  # convert string back to numeric
  columnNames = list(st.session_state.dataframe.columns)
  st.session_state.dataframe[columnNames[1:]] = st.session_state.dataframe[columnNames[1:]].astype(float)

def dataframe_with_selections(df):
  df_with_selections = df.copy()
  df_with_selections.insert(0, "Select", False)

  edited_df = st.data_editor(
    df_with_selections,
    column_config={"Select": st.column_config.CheckboxColumn(required=True),
                   },
    use_container_width=True,
    hide_index=True,
    height=800
  )

  selected_rows = edited_df[edited_df.Select]
  return selected_rows.drop('Select', axis=1)

initSessionStateVariables()

with st.sidebar:
  uploadedFile = st.file_uploader("Choose a OHM log file (*.csv)", type=['csv'])
  if uploadedFile is not None:
    fileUploaded(uploadedFile)
    
  if st.session_state.dataframe is None:
    st.stop()

  sensorNames = []
  for sn, aux in zip(list(st.session_state.dataframe.columns)[1:], st.session_state.basenames):
    sensorNames.append([sn, str(aux)])

  df = pd.DataFrame(sensorNames, columns=["Sensors", "Aux"])
  sensors = dataframe_with_selections(df)

sensors = sensors["Sensors"]
if "Time" in sensors:
  sensors.remove("Time")

with st.expander("Usage"):
  st.write("Upload a OpenHardwareMonitor log file via the side bar and then select sensors to view.")

if len(sensors) > 0:
  timeStart = st.session_state.dataframe["Time"][0]
  timeEnd = st.session_state.dataframe["Time"][len(st.session_state.dataframe["Time"])-1]

  start_time, end_time = st.select_slider("Select a time period to visualize",
                                          options=st.session_state.dataframe["Time"],
                                          value=(timeStart, timeEnd))

  sub_df = st.session_state.dataframe[st.session_state.dataframe["Time"] >= start_time]
  sub_df = sub_df[sub_df["Time"] <= end_time]

  st.line_chart(sub_df,
                x="Time",
                y=sensors,
                height=500)

  # select only min, max, and mean from describe()
  st.write(sub_df[sensors].describe().loc[['min', 'max', 'mean']])
