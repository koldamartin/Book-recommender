import pandas as pd
import numpy as np
from fuzzywuzzy import process


def match_books(user_input: str, df: pd.DataFrame, min_score: float = 0.8):
    # Use process.extractOne to get the best match
    book_titles = df['Book-Title'].unique()
    best_match = process.extractOne(user_input, book_titles)
    # Check if the best match score is above the minimum score
    if best_match and best_match[1] >= min_score:
        result = best_match[0]
    else:
        result = None
    return result


def recommend_books(df: pd.DataFrame, book_to_be_recommended: str) -> pd.DataFrame:
    """
    The recommend_books_new function identifies users who have read a specified book,
    finds other books these users have read, computes the correlation between the specified book and these other books,
    and returns a DataFrame with the recommended books, their correlation scores, and average ratings.
    """

    # Get relevant dataset of book's readers
    book_readers = df['User-ID'][df['Book-Title'] == book_to_be_recommended]
    book_readers = book_readers.tolist()
    book_readers = np.unique(book_readers)

    # Final dataset
    books_of_book_readers = df[(df['User-ID'].isin(book_readers))]
    number_of_rating_per_book = books_of_book_readers.groupby(['Book-Title']).agg('count').reset_index()

    # Iterate over the number_of_user_ratings to get the highest number,
    # while keeping at least 10 final records
    threshold = 0
    while True:
        books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= threshold]
        books_to_compare = books_to_compare.tolist()
        print(f"Threshold: {threshold}, Number of books to compare: {len(books_to_compare)}")
        if len(books_to_compare) <= 11:
            books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= threshold-1]
            break
        threshold += 1

    ratings_data_raw = books_of_book_readers[['User-ID', 'Book-Rating', 'Book-Title']][
        books_of_book_readers['Book-Title'].isin(books_to_compare)]

    # group by User and Book and compute mean
    ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

    # reset index to see User-ID in every row
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

    dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

    # Method 1: Using pandas corr() with pairwise complete observations
    correlations = dataset_for_corr.corrwith(dataset_for_corr[book_to_be_recommended], method='pearson')

    # Add average ratings for each book in dataset_for_corr
    average_ratings = ratings_data_raw_nodup.groupby('Book-Title')['Book-Rating'].mean().reset_index()

    # Create DataFrame with correlations
    correlations_df = pd.DataFrame({
        'Book-Title': correlations.index,
        'Correlation [%]': correlations.values,
    })

    # Merge correlations_df with average_ratings
    correlations_df = pd.merge(correlations_df, average_ratings, on='Book-Title')
    correlations_df = correlations_df.rename(columns={'Book-Rating': 'Average ratings'})

    # Sort by correlation value
    correlations_df = correlations_df.sort_values('Correlation [%]', ascending=False)

    # convert correlation column to percentage and limit to two decimals
    correlations_df['Correlation [%]'] = correlations_df['Correlation [%]'] * 100
    correlations_df['Correlation [%]'] = correlations_df['Correlation [%]'].round(2)

    # Remove the book being recommended from the list
    correlations_df = correlations_df[correlations_df['Book-Title'] != book_to_be_recommended]
    correlations_df = correlations_df.head(10)

    return correlations_df
