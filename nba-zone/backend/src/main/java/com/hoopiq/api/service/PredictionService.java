package com.hoopiq.api.service;

import com.hoopiq.api.model.Game;
import com.hoopiq.api.model.Prediction;
import com.hoopiq.api.repository.GameRepository;
import com.hoopiq.api.repository.PredictionRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class PredictionService {

    private final PredictionRepository predictionRepository;
    private final GameRepository gameRepository;

    public PredictionService(PredictionRepository predictionRepository, GameRepository gameRepository) {
        this.predictionRepository = predictionRepository;
        this.gameRepository = gameRepository;
    }

    public List<Prediction> getAllPredictions() {
        return predictionRepository.findAll();
    }

    public Optional<Prediction> getPredictionById(Long id) {
        return predictionRepository.findById(id);
    }

    public Optional<Prediction> getPredictionByGameId(Long gameId) {
        return predictionRepository.findByGameId(gameId);
    }

    public Prediction savePrediction(Prediction prediction) {
        return predictionRepository.save(prediction);
    }

    /**
     * Generate a mock prediction for a game.
     * In production, this would call the ML model.
     */
    public Prediction generatePrediction(Long gameId) {
        Game game = gameRepository.findById(gameId)
                .orElseThrow(() -> new RuntimeException("Game not found"));

        // Mock prediction logic - replace with actual ML model call
        double homeAdvantage = 0.54; // Home teams win ~54% of games
        double homeWinProb = homeAdvantage;
        double awayWinProb = 1 - homeWinProb;
        
        String predictedWinner = homeWinProb > awayWinProb 
                ? game.getHomeTeam().getAbbreviation() 
                : game.getAwayTeam().getAbbreviation();
        
        double confidence = Math.abs(homeWinProb - 0.5) * 2 * 100; // 0-100 scale

        Prediction prediction = new Prediction();
        prediction.setGame(game);
        prediction.setHomeWinProbability(homeWinProb * 100);
        prediction.setAwayWinProbability(awayWinProb * 100);
        prediction.setPredictedWinner(predictedWinner);
        prediction.setConfidence(confidence);

        return predictionRepository.save(prediction);
    }
}
