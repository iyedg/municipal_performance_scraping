# Municipal performance scraper

A tool that scrapes the performance data used in [The official collectivities in Tunisia](http://www.collectiviteslocales.gov.tn/) into a SQLite database.

## Usage

### Database prep

```bash
munperf db reset
```

### Loading data

#### Governorates

```bash
munperf load governorates
```

#### Municipalities

```bash
munperf load municipalities
```

#### All

```bash
munperf load all
```
