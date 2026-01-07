package com.hoopiq.api.config;

import com.hoopiq.api.model.Player;
import com.hoopiq.api.model.Team;
import com.hoopiq.api.repository.PlayerRepository;
import com.hoopiq.api.repository.TeamRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataLoader implements CommandLineRunner {

    private final TeamRepository teamRepository;
    private final PlayerRepository playerRepository;

    public DataLoader(TeamRepository teamRepository, PlayerRepository playerRepository) {
        this.teamRepository = teamRepository;
        this.playerRepository = playerRepository;
    }

    @Override
    public void run(String... args) {
        loadTeams();
        loadPlayers();
    }

    private void loadTeams() {
        if (teamRepository.count() > 0) return;

        Team[] teams = {
            createTeam("Lakers", "Los Angeles", "LAL", "West", "Pacific", "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg", 1947, 17),
            createTeam("Celtics", "Boston", "BOS", "East", "Atlantic", "https://cdn.nba.com/logos/nba/1610612738/primary/L/logo.svg", 1946, 18),
            createTeam("Warriors", "Golden State", "GSW", "West", "Pacific", "https://cdn.nba.com/logos/nba/1610612744/primary/L/logo.svg", 1946, 7),
            createTeam("Bulls", "Chicago", "CHI", "East", "Central", "https://cdn.nba.com/logos/nba/1610612741/primary/L/logo.svg", 1966, 6),
            createTeam("Heat", "Miami", "MIA", "East", "Southeast", "https://cdn.nba.com/logos/nba/1610612748/primary/L/logo.svg", 1988, 3),
            createTeam("Nuggets", "Denver", "DEN", "West", "Northwest", "https://cdn.nba.com/logos/nba/1610612743/primary/L/logo.svg", 1967, 1),
            createTeam("Bucks", "Milwaukee", "MIL", "East", "Central", "https://cdn.nba.com/logos/nba/1610612749/primary/L/logo.svg", 1968, 2),
            createTeam("Suns", "Phoenix", "PHX", "West", "Pacific", "https://cdn.nba.com/logos/nba/1610612756/primary/L/logo.svg", 1968, 0),
            createTeam("Mavericks", "Dallas", "DAL", "West", "Southwest", "https://cdn.nba.com/logos/nba/1610612742/primary/L/logo.svg", 1980, 1),
            createTeam("76ers", "Philadelphia", "PHI", "East", "Atlantic", "https://cdn.nba.com/logos/nba/1610612755/primary/L/logo.svg", 1946, 3),
            createTeam("Knicks", "New York", "NYK", "East", "Atlantic", "https://cdn.nba.com/logos/nba/1610612752/primary/L/logo.svg", 1946, 2),
            createTeam("Nets", "Brooklyn", "BKN", "East", "Atlantic", "https://cdn.nba.com/logos/nba/1610612751/primary/L/logo.svg", 1967, 0)
        };

        for (Team team : teams) {
            teamRepository.save(team);
        }
        System.out.println("Loaded " + teams.length + " teams");
    }

    private Team createTeam(String name, String city, String abbr, String conference, String division, String logo, int founded, int championships) {
        Team team = new Team();
        team.setName(name);
        team.setCity(city);
        team.setAbbreviation(abbr);
        team.setConference(conference);
        team.setDivision(division);
        team.setLogo(logo);
        team.setFounded(founded);
        team.setChampionships(championships);
        return team;
    }

    private void loadPlayers() {
        if (playerRepository.count() > 0) return;

        Team lal = teamRepository.findByAbbreviation("LAL").orElse(null);
        Team gsw = teamRepository.findByAbbreviation("GSW").orElse(null);
        Team phx = teamRepository.findByAbbreviation("PHX").orElse(null);
        Team mil = teamRepository.findByAbbreviation("MIL").orElse(null);
        Team dal = teamRepository.findByAbbreviation("DAL").orElse(null);
        Team den = teamRepository.findByAbbreviation("DEN").orElse(null);
        Team phi = teamRepository.findByAbbreviation("PHI").orElse(null);
        Team bos = teamRepository.findByAbbreviation("BOS").orElse(null);
        Team mia = teamRepository.findByAbbreviation("MIA").orElse(null);

        Player[] players = {
            createPlayer("LeBron", "James", lal, "SF", 23, "6-9", "250", "St. Vincent-St. Mary HS", "USA", 25.7, 7.3, 8.3, "https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png"),
            createPlayer("Stephen", "Curry", gsw, "PG", 30, "6-2", "185", "Davidson", "USA", 29.4, 6.1, 6.3, "https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png"),
            createPlayer("Kevin", "Durant", phx, "SF", 35, "6-10", "240", "Texas", "USA", 29.1, 6.7, 5.0, "https://cdn.nba.com/headshots/nba/latest/1040x760/201142.png"),
            createPlayer("Giannis", "Antetokounmpo", mil, "PF", 34, "6-11", "243", "None", "Greece", 31.1, 11.8, 5.7, "https://cdn.nba.com/headshots/nba/latest/1040x760/203507.png"),
            createPlayer("Luka", "Doncic", dal, "PG", 77, "6-7", "230", "None", "Slovenia", 32.4, 8.6, 8.0, "https://cdn.nba.com/headshots/nba/latest/1040x760/1629029.png"),
            createPlayer("Nikola", "Jokic", den, "C", 15, "6-11", "284", "None", "Serbia", 24.5, 11.8, 9.8, "https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png"),
            createPlayer("Joel", "Embiid", phi, "C", 21, "7-0", "280", "Kansas", "Cameroon", 33.1, 10.2, 4.2, "https://cdn.nba.com/headshots/nba/latest/1040x760/203954.png"),
            createPlayer("Jayson", "Tatum", bos, "SF", 0, "6-8", "210", "Duke", "USA", 30.1, 8.8, 4.6, "https://cdn.nba.com/headshots/nba/latest/1040x760/1628369.png"),
            createPlayer("Anthony", "Davis", lal, "PF", 3, "6-10", "253", "Kentucky", "USA", 24.7, 12.6, 3.5, "https://cdn.nba.com/headshots/nba/latest/1040x760/203076.png"),
            createPlayer("Jimmy", "Butler", mia, "SF", 22, "6-7", "230", "Marquette", "USA", 22.9, 5.9, 5.3, "https://cdn.nba.com/headshots/nba/latest/1040x760/202710.png"),
            createPlayer("Devin", "Booker", phx, "SG", 1, "6-5", "206", "Kentucky", "USA", 27.1, 4.5, 6.9, "https://cdn.nba.com/headshots/nba/latest/1040x760/1626164.png"),
            createPlayer("Jaylen", "Brown", bos, "SG", 7, "6-6", "223", "California", "USA", 26.6, 6.9, 3.5, "https://cdn.nba.com/headshots/nba/latest/1040x760/1627759.png")
        };

        for (Player player : players) {
            playerRepository.save(player);
        }
        System.out.println("Loaded " + players.length + " players");
    }

    private Player createPlayer(String firstName, String lastName, Team team, String position, int jersey, String height, String weight, String college, String country, double ppg, double rpg, double apg, String image) {
        Player player = new Player();
        player.setFirstName(firstName);
        player.setLastName(lastName);
        player.setTeam(team);
        player.setPosition(position);
        player.setJerseyNumber(jersey);
        player.setHeight(height);
        player.setWeight(weight);
        player.setCollege(college);
        player.setCountry(country);
        player.setPpg(ppg);
        player.setRpg(rpg);
        player.setApg(apg);
        player.setImageUrl(image);
        player.setIsActive(true);
        return player;
    }
}
