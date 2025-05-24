# Daten einlesen
karten <- read.csv("./WAHR/data/Mythical_Island.csv", stringsAsFactors = FALSE)
karten_god_pack <- read.csv("./WAHR/data/Mythical_Island_god_pack.csv", stringsAsFactors = FALSE)

parse_percent_column <- function(x) {
  # Wenn leer oder nur Spaces → 0 setzen
  x[trimws(x) == ""] <- "0%"
  # Prozentzeichen entfernen und umrechnen in Dezimalzahl
  as.numeric(sub("%", "", x)) / 100
}

alle_karten <- karten$Name
# wahrscheinlichkeiten dass karten in slot 1-3, 4 oder 5 gezogen werden
prob_1_3 <- parse_percent_column(karten$First.third.cards)
prob_4   <- parse_percent_column(karten$Fourth.card)
prob_5   <- parse_percent_column(karten$Fifth.card)

prob_total <- prob_1_3 + prob_4 + prob_5

alle_karten_god <- karten_god_pack$Name
# wahrscheinlichkeiten dass god_pack karten in slot 1-3, 4 oder 5 gezogen werden
prob_1_3_g <- parse_percent_column(karten_god_pack$First.third.cards)
prob_4_g   <- parse_percent_column(karten_god_pack$Fourth.card)
prob_5_g   <- parse_percent_column(karten_god_pack$Fifth.card)

prob_total_god_pack <- prob_1_3_g + prob_4_g + prob_5_g


# Zählt, wie viele Karten überhaupt eine Chance > 0 haben gezogen zu werden.
prob_total
cat("Karten mit > 0 Drop-Chance: ", sum(prob_total > 0), "/", length(alle_karten), "\n")

# Simuliert ein Kartenpack mit 5 Karten, möglichkeit god pack oder normales pack zu ziehen
ziehe_pack <- function() {
  is_godpack <- runif(1) < 0.0005  # 0.05% Chance
  
  if (is_godpack) {
    c(
      sample(all_karten_god, size = 3, replace = TRUE, prob = prob_1_3_g),
      sample(all_karten_god, size = 1, replace = TRUE, prob = prob_4_g),
      sample(all_karten_god, size = 1, replace = TRUE, prob = prob_5_g)
    )
  } else {
    c(
      sample(alle_karten, size = 3, replace = TRUE, prob = prob_1_3),
      sample(alle_karten, size = 1, replace = TRUE, prob = prob_4),
      sample(alle_karten, size = 1, replace = TRUE, prob = prob_5)
    )
  }
}

# Schnelle Zieh-Funktion, simuliert packs_pro_tag * tage Ziehungen (z.B. 2 Packs pro Tag × 30 Tage).
simuliere_jahr_mit_slots <- function(packs_pro_tag, tage = 30) {
  gezogen <- replicate(packs_pro_tag * tage, ziehe_pack(), simplify = FALSE)
  gezogen <- unlist(gezogen)  # flatten
  length(unique(gezogen))
}


N <- 1000
tage_vektor <- c(7, 14, 30)
kosten_premium_pro_monat <- 10

# Simulationsergebnisse initialisieren, gratis = 2 packs pro tag, premium = 4 packs pro tag
ergebnisse <- list()

for (tage in tage_vektor) {
  gratis <- as.numeric(replicate(N, simuliere_jahr_mit_slots(2, tage = tage)))
  premium <- as.numeric(replicate(N, simuliere_jahr_mit_slots(4, tage = tage)))
  
  # Mittelwert der Differenz (extra Karten)
  mean_diff <- mean(premium - gratis, na.rm = TRUE)
  
  # Falls NA oder NaN, setze auf 0
  if (is.na(mean_diff) || is.nan(mean_diff)) {
    mean_diff <- 0
  }
  
  # Kosten berechnen
  kosten <- (tage / 30) * kosten_premium_pro_monat
  
  # Kosten pro extra Karte nur berechnen, wenn sinnvoll
  kosten_pro_extra <- if (mean_diff > 0) kosten / mean_diff else NA
  
  # Ergebnisse speichern
  ergebnisse[[as.character(tage)]] <- list(
    tage = tage,
    gratis = gratis,
    premium = premium,
    kosten = kosten,
    extra_karten = mean_diff,
    kosten_pro_extra = kosten_pro_extra
  )
}


library(ggplot2)

for (tage in tage_vektor) {
  df <- data.frame(
    Karten = c(ergebnisse[[as.character(tage)]]$gratis,
               ergebnisse[[as.character(tage)]]$premium),
    Modell = rep(c("Gratis", "Premium"), each = N)
  )

  p <- ggplot(df, aes(x = Karten, fill = Modell)) +
    geom_bar(position = "dodge", color = "black") +
    labs(
      title = paste("Verteilung der Kartenzahl nach", tage, "Tagen"),
      subtitle = paste0("Ø Extra Karten mit Premium: ",
                        round(ergebnisse[[as.character(tage)]]$extra_karten, 1),
                        " | Kosten pro Extra-Karte: $",
                        round(ergebnisse[[as.character(tage)]]$kosten_pro_extra, 2)),
      x = "Anzahl verschiedener Karten",
      y = "Anzahl Simulationen"
    ) +
    theme_minimal() +
    theme(legend.position = "top")

  print(p)
}


for (tage in tage_vektor) {
  res <- ergebnisse[[as.character(tage)]]
  
  cat("🔹", tage, "Tage:\n")
  cat("  Premium-Kosten: $", round(res$kosten, 2), "\n")
  
  if (is.numeric(res$extra_karten) && !is.na(res$extra_karten)) {
    cat("  ∅ Extra Karten: ", round(res$extra_karten, 1), "\n")
    cat("  ∅ Kosten pro zusätzlicher Karte: $", round(res$kosten_pro_extra, 2), "\n\n")
  } else {
    cat("  Keine gültigen Daten für Extra-Karten.\n\n")
  }
}