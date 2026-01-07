# HoopIQ: NBA Analytics Platform

A comprehensive NBA statistics and analytics platform featuring game predictions, team/player statistics, and advanced metrics.

## 🏀 Features

- **Team Analytics**: Detailed team statistics and performance metrics
- **Player Stats**: Comprehensive player statistics with advanced filtering
- **Game Predictions**: Machine learning-powered game outcome predictions
- **Historical Data**: Access to historical NBA data and trends
- **Interactive Dashboard**: User-friendly interface with responsive design
- **Player Statistics**: Detailed stats for all NBA players
- **Team Statistics**: Team performance metrics and analytics
- **Game Center**: Live scores, schedules, and results
- **Standings**: Conference and division standings
- **Player Comparisons**: Compare stats between players
- **Game Predictions**: Machine learning-powered game outcome predictions

## Tech Stack

- **Frontend**: React.js with TypeScript, Redux, Material-UI
- **Backend**: Spring Boot (Java 17+)
- **Database**: PostgreSQL
- **Data Pipeline**: Python Web Scraping (BeautifulSoup/Scrapy)
- **Machine Learning**: Python (scikit-learn, pandas, numpy)
- **Deployment**: Docker, AWS/GCP (TBD)

## Project Structure

- `/frontend` - React.js application
- `/backend` - Spring Boot application
- `/scraper` - Python scripts for data collection
- `/ml` - Machine learning models and data processing

## Getting Started

### Prerequisites

- Node.js 16+
- Java 17+
- Python 3.9+
- PostgreSQL 14+

### Installation

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   ./mvnw spring-boot:run
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   npm start
   ```
4. Run the scraper:
   ```
   cd scraper
   pip install -r requirements.txt
   python main.py
   ```

## License

MIT

## Acknowledgments

- NBA API for providing basketball data
- Inspired by various sports analytics platforms
