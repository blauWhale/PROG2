# Daten einlesen
karten <- read.csv("./WAHR/data/Mythical_Island.csv", stringsAsFactors = FALSE)

parse_percent_column <- function(x) {
  # Wenn leer oder nur Spaces → 0 setzen
  x[trimws(x) == ""] <- "0%"
  # Prozentzeichen entfernen und umrechnen
  as.numeric(sub("%", "", x)) / 100
}

alle_karten <- karten$Name
prob_1_3 <- parse_percent_column(karten$First.third.cards)
prob_4   <- parse_percent_column(karten$Fourth.card)
prob_5   <- parse_percent_column(karten$Fifth.card)


prob_total <- prob_1_3 + prob_4 + prob_5
cat("Karten mit > 0 Drop-Chance: ", sum(prob_total > 0), "/", length(alle_karten), "\n")

ziehe_pack <- function() {
  c(
    sample(alle_karten, size = 3, replace = TRUE, prob = prob_1_3),
    sample(alle_karten, size = 1, replace = TRUE, prob = prob_4),
    sample(alle_karten, size = 1, replace = TRUE, prob = prob_5)
  )
}


# Schnelle Zieh-Funktion
simuliere_jahr_mit_slots <- function(packs_pro_tag, tage = 30) {
  gezogen <- replicate(packs_pro_tag * tage, ziehe_pack(), simplify = FALSE)
  gezogen <- unlist(gezogen)  # flatten
  length(unique(gezogen))
}


N <- 1000
tage_vektor <- c(30)
kosten_premium_pro_monat <- 10

# Simulationsergebnisse initialisieren
ergebnisse <- list()

for (tage in tage_vektor) {
  gratis <- replicate(N, simuliere_jahr_mit_slots(2, tage = tage))
  premium <- replicate(N, simuliere_jahr_mit_slots(4, tage = tage))

  ergebnisse[[as.character(tage)]] <- list(
    tage = tage,
    gratis = gratis,
    premium = premium,
    kosten = (tage / 30) * kosten_premium_pro_monat,
    extra_karten = mean(premium - gratis),
    kosten_pro_extra = ((tage / 30) * kosten_premium_pro_monat) / mean(premium - gratis)
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
  cat("  Premium-Kosten: $", res$kosten, "\n")
  cat("  ∅ Extra Karten: ", round(res$extra_karten, 1), "\n")
  cat("  ∅ Kosten pro zusätzlicher Karte: $", round(res$kosten_pro_extra, 2), "\n\n")
}
