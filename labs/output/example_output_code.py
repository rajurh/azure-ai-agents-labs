import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# solution plan
# i. Convert 'Date' column to datetime
# ii. Group data by 'Segment' and 'Product' and calculate total sales
# iii. Create a bar plot to visualize the sales by segment for each product

def plot(data: pd.DataFrame):
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    data = data[pd.notna(data['Date'])]

    sales_by_segment_product = data.groupby(['Segment', 'Product'])[' Sales'].sum().reset_index()

    plt.figure(figsize=(12, 8))
    sns.barplot(x='Product', y=' Sales', hue='Segment', data=sales_by_segment_product)
    plt.xlabel('Product')
    plt.ylabel('Total Sales')
    plt.title('What are the key trends regarding product sales by segment per product type ?', wrap=True)
    plt.legend(title='Segment')
    return plt

chart = plot(data)