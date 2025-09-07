# MadLife Event Search - Refactored Architecture

## Project Structure

The application has been refactored into a modular architecture for better scalability and maintainability:

```
MadLife/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration constants and settings
├── utils.py                    # Utility functions for data processing
├── embedding_manager.py        # Vector database and embeddings management
├── apiManager.py              # Data loading and API management
├── visualizations/             # Visualization components package
│   ├── __init__.py            # Package initialization with exports
│   ├── calendar_export.py     # Calendar export functionality
│   ├── charts.py              # Charts and analytics visualizations
│   ├── event_detail.py        # Detailed event view component
│   └── search_results.py      # Search results display component
├── chroma_db/                 # Vector database storage
├── pruebas/                   # Testing and data analysis notebooks
└── README.md                  # Project documentation
```

## Key Features

### 🎯 Event Visualization
- **Detailed Event View**: Click on any event to see comprehensive details
- **Calendar Export**: Export events to Google Calendar, Outlook, Yahoo, or download as ICS
- **Interactive Search Results**: Clickable event titles with quick actions

### 📊 Analytics Dashboard
- **Similarity Charts**: Visual representation of search relevance
- **Distribution Charts**: Events by district, type, and price
- **Summary Metrics**: Key statistics about search results
- **Timeline View**: Events distributed over time

### 🔍 Advanced Filtering
- **Metadata Filters**: Filter by district, type, venue, and price
- **Date Range**: Filter events by date range
- **Search Configuration**: Customize number of results and visualizations

### 📅 Calendar Integration
- **Multiple Formats**: Support for Google Calendar, Outlook, Yahoo Calendar
- **ICS Export**: Download standard calendar files
- **Quick Export**: One-click calendar addition from search results

## Module Documentation

### `visualizations/` Package

#### `calendar_export.py`
- `create_calendar_export_links()`: Generate calendar URLs for all platforms
- `generate_ics_content()`: Create ICS file content
- `render_calendar_export_buttons()`: HTML buttons for calendar export

#### `charts.py`
- `create_similarity_chart()`: Similarity score visualization
- `create_district_distribution_chart()`: District distribution pie chart
- `create_event_type_chart()`: Event type bar chart
- `render_analytics_dashboard()`: Complete analytics dashboard

#### `event_detail.py`
- `display_event_detail()`: Comprehensive event detail view
- `display_event_preview()`: Compact event preview for lists

#### `search_results.py`
- `display_search_results()`: Interactive search results display
- `display_search_summary()`: Results summary sidebar
- `display_no_results_message()`: Helpful no-results screen

### `config.py`
- Application configuration constants
- UI messages and text
- Color schemes and styling
- Date formats and field mappings

### `utils.py`
- Data processing utilities
- Filter creation and application
- Session state management
- Export data preparation

## Usage

### Running the Application
```bash
streamlit run app.py
```

### Adding New Visualizations
1. Create a new file in `visualizations/` directory
2. Add your visualization functions
3. Import in `visualizations/__init__.py`
4. Use in `app.py` main function

### Extending Functionality
- **New Calendar Platforms**: Add to `calendar_export.py`
- **Additional Charts**: Extend `charts.py`
- **Custom Filters**: Add to `utils.py`
- **New Event Fields**: Update `config.py` field mappings

## Dependencies

```python
streamlit           # Web application framework
pandas             # Data manipulation
plotly             # Interactive charts
chromadb           # Vector database
sentence-transformers  # Text embeddings
```

## Future Enhancements

- [ ] User favorites and saved searches
- [ ] Event recommendations based on preferences
- [ ] Social sharing integration
- [ ] Advanced analytics with machine learning insights
- [ ] Mobile-responsive design improvements
- [ ] Multi-language support

## Contributing

When adding new features:
1. Follow the modular structure
2. Add appropriate documentation
3. Update configuration in `config.py`
4. Create utility functions in `utils.py`
5. Test thoroughly with different event types
