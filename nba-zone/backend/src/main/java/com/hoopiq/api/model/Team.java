package com.hoopiq.api.model;

import jakarta.persistence.*;

@Entity
@Table(name = "teams")
public class Team {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String city;

    @Column(nullable = false, unique = true)
    private String abbreviation;

    @Column(nullable = false)
    private String conference;

    @Column(nullable = false)
    private String division;

    private String logo;

    private Integer founded;

    private Integer championships;

    public Team() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    public String getAbbreviation() { return abbreviation; }
    public void setAbbreviation(String abbreviation) { this.abbreviation = abbreviation; }
    public String getConference() { return conference; }
    public void setConference(String conference) { this.conference = conference; }
    public String getDivision() { return division; }
    public void setDivision(String division) { this.division = division; }
    public String getLogo() { return logo; }
    public void setLogo(String logo) { this.logo = logo; }
    public Integer getFounded() { return founded; }
    public void setFounded(Integer founded) { this.founded = founded; }
    public Integer getChampionships() { return championships; }
    public void setChampionships(Integer championships) { this.championships = championships; }
}
