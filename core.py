import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import streamlit as st

# Инициализация списка желаемого и количества отображаемых товаров
if 'wishlist' not in st.session_state:
    st.session_state['wishlist'] = []

if 'shown_count' not in st.session_state:
    st.session_state['shown_count'] = 20  # Количество товаров, которые показываются сразу


def main():
    # Header
    # header_image = Image.open('Images/h&mBanner.jpeg')
    # st.image(header_image)

    # Sidebar
    st.sidebar.title('H&M Article Recommendations')

    # Загрузка данных
    articles_df = pd.read_csv('Data/articles.csv.zip', index_col='article_id')
    articles_df2 = pd.read_csv('Data/articles.csv.zip')
    meta_data = pd.read_csv('Data/out_content.zip')

    # Загрузка трех моделей коллаборативной фильтрации
    model_svd = pickle.load(open('Model/collaborative_model_svd.sav', 'rb'))
    model_nmf = pickle.load(open('Model/collaborative_model_NMF.sav', 'rb'))
    model_svdpp = pickle.load(open('Model/collaborative_model_svdpp.sav', 'rb'))

    # Функция для добавления товаров в список желаемого
    def add_to_wishlist(article_id):
        if article_id not in st.session_state['wishlist']:
            st.session_state['wishlist'].append(article_id)

    # Функция для удаления товара из списка желаемого
    def remove_from_wishlist(article_id):
        if article_id in st.session_state['wishlist']:
            st.session_state['wishlist'].remove(article_id)

    # Функция для генерации рекомендаций на основе коллаборативной модели
    def generate_recommendations_from_wishlist(n_recs, model):
        if not st.session_state['wishlist']:
            st.write("Ваш список желаемого пуст.")
            return None
        recommendations = []
        for article_id in st.session_state['wishlist']:
            article_recommendations = articles_df2.copy()
            article_recommendations['score'] = article_recommendations['article_id'].apply(
                lambda x: model.predict(st.session_state['wishlist'][0], x).est)  # Пример для 1-го пользователя
            article_recommendations = article_recommendations.sort_values(by='score', ascending=False).head(n_recs)
            recommendations.append(article_recommendations)
        recommendations_df = pd.concat(recommendations)
        return recommendations_df

    # Функция для отображения изображений (по 5 штук в строке)
    def print_image_cf(results_cf):
        images_per_row = 5
        total = len(results_cf)
        rows = (total // images_per_row) + int(total % images_per_row > 0)

        fig, axarr = plt.subplots(rows, images_per_row, figsize=(20, 10 * rows))
        article_id_cf = results_cf['article_id']

        if rows == 1:
            axarr = [axarr]

        i = 0
        for index, data in enumerate(article_id_cf):
            row = i // images_per_row
            col = i % images_per_row
            desc = articles_df2[articles_df2['article_id'] == data]['detail_desc'].iloc[0]
            desc_list = desc.split(' ')
            for j, elem in enumerate(desc_list):
                if j > 0 and j % 5 == 0:
                    desc_list[j] = desc_list[j] + '\n'
            desc = ' '.join(desc_list)
            img = mpimg.imread(
                f'Data/h-and-m-personalized-fashion-recommendations/images/0{str(data)[:2]}/0{int(data)}.jpg')

            axarr[row][col].imshow(img)
            axarr[row][col].set_xticks([])
            axarr[row][col].set_yticks([])
            axarr[row][col].grid(False)
            # axarr[row][col].set_xlabel(desc, fontsize=14)
            i += 1

        for j in range(i, rows * images_per_row):
            fig.delaxes(axarr[j // images_per_row][j % images_per_row])

        st.pyplot(fig)

    # Страница списка желаемого с возможностью удаления товаров и отрисовки картинок
    def wishlist_page():
        st.title("Ваш список желаемого")
        if not st.session_state['wishlist']:
            st.write("Ваш список желаемого пуст.")
            return

        images_per_row = 5
        for i, article_id in enumerate(st.session_state['wishlist']):
            # Получаем информацию о статье
            article_info = articles_df2[articles_df2['article_id'] == article_id].iloc[0]
            img_path = f'Data/h-and-m-personalized-fashion-recommendations/images/0{str(article_id)[:2]}/0{int(article_id)}.jpg'

            # Отображаем картинку и информацию о товаре
            cols = st.columns([1, 4])
            with cols[0]:
                st.image(img_path, width=150)
            with cols[1]:
                st.write(f"Товар ID: {article_id} - {article_info['prod_name']}")
                if st.button(f"Удалить {article_id}", key=f"remove_{article_id}"):
                    remove_from_wishlist(article_id)

    # Главная страница с товарами и выбором тем
    def main_page():
        st.subheader("Выберите товары для добавления в список желаемого:")

        # Выбор тем (категорий)
        categories = articles_df2['product_type_name'].unique()
        st.sidebar.subheader('Выберите интересные вам категории')
        selected_categories = st.sidebar.multiselect('Категории', categories)

        # Фильтрация товаров по выбранным категориям
        if selected_categories:
            filtered_articles = articles_df2[articles_df2['product_type_name'].isin(selected_categories)]
        else:
            filtered_articles = articles_df2.copy()

        total_items = len(filtered_articles)

        # Отображение товаров
        for index, row in filtered_articles.iterrows():
            if index >= st.session_state['shown_count']:
                break
            st.image(
                f'Data/h-and-m-personalized-fashion-recommendations/images/0{str(row["article_id"])[:2]}/0{int(row["article_id"])}.jpg',
                width=150)
            st.write(row['prod_name'])
            if st.button(f"Добавить {row['article_id']} в список желаемого", key=f"wishlist_{index}"):
                add_to_wishlist(row['article_id'])

        # Кнопка "Показать еще"
        if st.session_state['shown_count'] < total_items:
            if st.button("Показать еще"):
                st.session_state['shown_count'] += 20

        # Выбор модели рекомендаций
        st.sidebar.subheader("Выберите модель для рекомендаций")
        model_type = st.sidebar.selectbox("Модель", ["SVD", "NMF", "SVD++"])

        # Кнопка рекомендаций
        if st.button("Получить рекомендации"):
            if model_type == "SVD":
                recommendations = generate_recommendations_from_wishlist(5, model_svd)
            elif model_type == "NMF":
                recommendations = generate_recommendations_from_wishlist(5, model_nmf)
            elif model_type == "SVD++":
                recommendations = generate_recommendations_from_wishlist(5, model_svdpp)

            if recommendations is not None:
                st.subheader("Рекомендации:")
                st.table(recommendations[['prod_name', 'product_type_name', 'product_group_name']])
                result_image = print_image_cf(recommendations)

    # Sidebar Navigation
    page_names = ['Главная страница', 'Список желаемого']
    page = st.sidebar.radio('Навигация', page_names)

    if page == 'Главная страница':
        main_page()
    elif page == 'Список желаемого':
        wishlist_page()