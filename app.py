import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter


st.set_page_config(layout='wide',page_title='Netflix Dashboard')
st.title('Netflix Dashboard')

#File uploading task
uploaded_file=st.file_uploader("Upload your Netflix CSV file",type=['csv'])

if uploaded_file is not None:
        df=pd.read_csv(uploaded_file)
        st.success("File uploaded sucessfully")

        #Setting up the sidebar
        st.sidebar.header("Filter Options")

        #Setting up the sidebar for dropdown box
        type_filter=st.sidebar.selectbox("select content type:",options=["All","Movie","TV Show"],index=0)

        #Filtering the data
        df.fillna({'director':'Unknown','cast':'Unknoown','country':'Unknown'},inplace=True)
        df.dropna(subset=['date_added','rating','duration'],inplace=True)
        df['date_added']=df['date_added'].str.strip()
        df['date_added']=pd.to_datetime(df['date_added'],format='%B %d, %Y')
        df['year_added']=df['date_added'].dt.year

        #Setting up the slider for year range
        year_min=int(df['year_added'].min())
        year_max=int(df['year_added'].max())
        year_range=st.sidebar.slider("Select year range",min_value=year_min,max_value=year_max,value=(year_min,year_max))

        #Setting up the side bar for search bar
        search_input=st.sidebar.text_input("Search by Title")
        

        #Converting the dataframe based on the selction made in the side bar dropdown box
        if type_filter != "All":
            df = df[df['type'] == type_filter]
            
        #Converting the dataframe based on the selection made in the side bar range filter    
        df=df[(df['year_added']>=year_range[0])&(df['year_added']<=year_range[1])]

        #Converting the dataframe based on the searched title
        if search_input:
                df=df[df['title'].str.contains(search_input, case=False, na=False)]

        #Calculating year counts
        yearly_counts = df['year_added'].value_counts().sort_index()
        year_names = yearly_counts.index
        year_count = yearly_counts.values

        #Calculating countries count
        country_series=df['country'].str.split(', ')
        all_countries=[country for sublist in country_series for country in sublist if country!='Unknown']
        country_counts=Counter(all_countries)
        top_countries=country_counts.most_common(10)

        country_names=[item[0] for item in top_countries]
        country_values=[item[1] for item in top_countries]

        #Calculating genre count
        genre_series=df['listed_in'].str.split(', ')
        genre_list=[genre for sublist in genre_series for genre in sublist]
        genre_count=Counter(genre_list)
        top_genre=genre_count.most_common(10)
        genre_names=[item[0] for item in top_genre]
        genre_values=[item[1] for item in top_genre]

        #Key points 
        total_titles = len(df)
        movie_count = (df['type'] == 'Movie').sum()
        tv_count = (df['type'] == 'TV Show').sum()
        country_set = df['country'].dropna().str.split(', ').explode().nunique()

        st.markdown("Key Metrics")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Titles", total_titles)
        k2.metric("Movies", movie_count)
        k3.metric("TV Shows", tv_count)
        k4.metric("Countries", country_set)

        

        #Displaying the filtered dataset
        st.write("Here is the quick look at your data:")
        st.dataframe(df.head())
        st.write(f"Total entries shown:",df.shape[0])


        # Now count vs movie/Tv Show
        movietv_counts=df['type'].value_counts().values
        movietv_names=df['type'].value_counts().index


        # Set dark background for matplotlib
        plt.style.use('dark_background')

        

        #Pie chart and bar plot for movies vs TV shows
        col1,col2=st.columns(2)
        pie_fig = px.pie(
        names=movietv_names,
        values=movietv_counts,
        title="Movie vs TV Show",
        color_discrete_sequence=['#E50914', '#b3b3b3'],
        hole=0.3  # donut style (sexy)
    )
        bar_fig = px.bar(
        x=movietv_names,
        y=movietv_counts,
        labels={'x':'Content Type', 'y':'Count'},
        title="Content Type Count",
        color=movietv_names,
        color_discrete_map={'Movie':'#E50914', 'TV Show':'#b3b3b3'}
    )

        bar_fig.update_layout(
            plot_bgcolor='#221f1f',
            paper_bgcolor='#221f1f',
            font_color='white'
        )

        with col1:

            st.subheader("Movie vs TV Show (Interactive)")
            st.plotly_chart(pie_fig, use_container_width=True)


        with col2:
            
            st.subheader("Content Count (Interactive)")
            st.plotly_chart(bar_fig, use_container_width=True)


        #Line plot for No of movies added per year 
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=year_names,
            y=year_count,
            mode='lines+markers',
            name='Titles Added',
            line=dict(color='#E50914', width=3),
            marker=dict(color='white', size=6)
        ))

        line_fig.update_layout(
            plot_bgcolor='#221f1f',
            paper_bgcolor='#221f1f',
            font=dict(color='white'),
            title='📅 Netflix Additions per Year',
            xaxis=dict(title='Year',tickmode='linear',dtick=1),
            yaxis=dict(title='Number of Titles'),
        )

        st.plotly_chart(line_fig, use_container_width=True)


        # Country Plot


        country_fig=px.bar(
                x=country_values,
                y=country_names,
                orientation='h',
                title='Top 10 Content Producing Countries',
                color=country_names,
                color_discrete_sequence=px.colors.sequential.Reds,

                )
        country_fig.update_layout(
                plot_bgcolor='#221f1f',
                paper_bgcolor='#221f1f',
                font=dict(color='white'),
                xaxis=dict(title='Number of Titles'),
                yaxis=dict(title='Country', autorange='reversed')


                )
        st.plotly_chart(country_fig, use_container_width=True)

        # Genre Plot


        genre_fig=px.bar(
                x=genre_values,
                y=genre_names,
                orientation='h',
                title='Top 10 Netflix genres',
                color=genre_names,
                color_discrete_sequence=px.colors.sequential.Reds,

                )
        genre_fig.update_layout(
                plot_bgcolor='#221f1f',
                paper_bgcolor='#221f1f',
                font=dict(color='white'),
                xaxis=dict(title='Number of Titles'),
                yaxis=dict(title='Genre', autorange='reversed')


                )
        st.plotly_chart(genre_fig, use_container_width=True)


        #Download the filtered csv dataset
        def convert_df_to_csv(data):
            return data.to_csv(index=False).encode('utf-8')

        csv_data = convert_df_to_csv(df)

        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name='filtered_netflix_data.csv',
            mime='text/csv'
        )


        

else:
    st.info("Upload a CSV file to get started.")
    

