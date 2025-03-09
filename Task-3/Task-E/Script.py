# %% Cell: Multimodal Correlation Analysis
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

flag_df = pd.DataFrame({
    'Country': ['India', 'USA', 'France', 'Japan', 'Brazil'],
    'Aspect_Ratio': [1.5, 1.6, 1.33, 1.5, 1.5],
    'Dominant_Hue': [30, 210, 60, 240, 0]  # in degrees (example: 30 for orange, 210 for blue, etc.)
})

# For anthem text, we might have a sentiment score and average word length.
text_df = pd.DataFrame({
    'Country': ['India', 'USA', 'France', 'Japan', 'Brazil'],
    'Sentiment_Score': [0.1, 0.05, 0.2, 0.15, 0.0],  # sample sentiment values
    'Avg_Word_Length': [4.2, 4.0, 4.3, 4.1, 4.0]
})

# For anthem audio, we might have features like tempo and duration.
audio_df = pd.DataFrame({
    'Country': ['India', 'USA', 'France', 'Japan', 'Brazil'],
    'Tempo': [120, 130, 115, 125, 110],  # BPM
    'Duration': [60, 65, 55, 70, 60]       # seconds
})

# --- Merge Dataframes ---
merged_df = flag_df.merge(text_df, on='Country').merge(audio_df, on='Country')
print("Merged DataFrame:")
print(merged_df)

# --- Compute Correlations ---
# Drop the 'Country' column for correlation analysis
corr_matrix = merged_df.drop(columns=['Country']).corr()
print("Correlation Matrix:")
print(corr_matrix)

# Visualize the correlation matrix using seaborn
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title("Multimodal Feature Correlation Matrix")
plt.show()

# --- Additional Plot: Scatter Plot ---
# For example, explore relationship between Dominant Hue (from flags) and Sentiment Score (from text)
plt.figure(figsize=(8,6))
sns.scatterplot(data=merged_df, x='Dominant_Hue', y='Sentiment_Score', 
                size='Tempo', hue='Aspect_Ratio', palette='viridis', sizes=(50,200))
plt.title("Dominant Hue vs. Sentiment Score\n(Size ~ Tempo, Color ~ Aspect Ratio)")
plt.xlabel("Dominant Hue (degrees)")
plt.ylabel("Sentiment Score")
plt.legend()
plt.show()

# --- Interactive Plotly Example ---
fig = px.scatter(merged_df, x="Dominant_Hue", y="Sentiment_Score", 
                 size="Tempo", color="Aspect_Ratio", hover_name="Country",
                 title="Interactive Scatter: Dominant Hue vs. Sentiment Score")
fig.show()
