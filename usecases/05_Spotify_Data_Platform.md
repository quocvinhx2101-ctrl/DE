# Spotify Data Platform Architecture

## Kiến Trúc Data Platform Của Spotify - The Audio Streaming Leader

---

## 🏢 TỔNG QUAN CÔNG TY

- **Quy mô:** 600+ triệu users, 220+ triệu premium subscribers
- **Content:** 100+ triệu tracks, 5+ triệu podcasts
- **Scale:** 70+ markets, billions of streams/day
- **Open source contributions:** Luigi, Backstage, Scio, Heroic

---

## 🏗️ TỔNG QUAN KIẾN TRÚC

```mermaid
graph TB
    subgraph Sources[" "]
        Sources_title["🎵 DATA SOURCES"]
        style Sources_title fill:none,stroke:none,color:#333,font-weight:bold
        S1[Stream Events]
        S2[Search Queries]
        S3[Playlist Actions]
        S4[Social Activity]
        S5[Audio Features]
    end

    subgraph Ingestion[" "]
        Ingestion_title["📥 INGESTION LAYER"]
        style Ingestion_title fill:none,stroke:none,color:#333,font-weight:bold
        PubSub["Cloud Pub/Sub<br/>Event Delivery"]
        Beam["Apache Beam<br/>Unified batch & streaming<br/>via Scio - Scala API"]
    end

    subgraph Storage[" "]
        Storage_title["💾 STORAGE LAYER"]
        style Storage_title fill:none,stroke:none,color:#333,font-weight:bold
        GCS["Data Lake<br/>GCS - Parquet"]
        BQ["BigQuery<br/>Analytics DWH"]
        Bigtable["Feature Store<br/>Bigtable<br/>ML Features"]
    end

    subgraph Compute[" "]
        Compute_title["⚙️ COMPUTE LAYER"]
        style Compute_title fill:none,stroke:none,color:#333,font-weight:bold
        Dataflow["Dataflow<br/>Apache Beam"]
        BQSQL["BigQuery<br/>SQL Analytics"]
        ML["ML Platform<br/>TensorFlow + Kubeflow"]
    end

    subgraph Products[" "]
        Products_title["🚀 DATA PRODUCTS"]
        style Products_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[Discover Weekly]
        P2[Radio Algorithm]
        P3[Wrapped Campaign]
        P4[Podcast Recommend]
        P5[Artist Analytics]
    end

    S1 & S2 & S3 & S4 & S5 --> PubSub
    PubSub --> Beam
    Beam --> GCS & BQ & Bigtable
    GCS & BQ & Bigtable --> Dataflow & BQSQL & ML
    Dataflow & BQSQL & ML --> P1 & P2 & P3 & P4 & P5
```

---

## 🔧 TECH STACK CHI TIẾT

### 1. Google Cloud Platform (Primary Cloud)

```
> **SPOTIFY ON GCP: SERVICES USED**
> 
> * **Compute:**
>   * Google Kubernetes Engine (GKE)
>   * Cloud Dataflow (Apache Beam)
>   * Cloud Composer (Airflow managed)
> 
> * **Storage:**
>   * Google Cloud Storage (GCS) - Data lake
>   * BigQuery - Analytics warehouse
>   * Cloud Bigtable - Feature serving
>   * Cloud Spanner - Global metadata
> 
> * **Streaming:**
>   * Cloud Pub/Sub - Event streaming
> 
> * **ML:**
>   * Vertex AI
>   * TensorFlow Extended (TFX)
> 
> **WHY GCP:**
> - **BigQuery:** Excellent for analytics at scale
> - **Dataflow:** Unified batch/streaming
> - **Managed services:** Less operational overhead
> - **Cost:** Competitive for their workload
```

### 2. Scio (Spotify Created)

```
> **SCIO - SCALA API FOR APACHE BEAM:**
> 
> **Example Pipeline:**
> ```scala
> import com.spotify.scio._
> import com.spotify.scio.bigquery._
> 
> object StreamsETL {
>   def main(args: Array[String]): Unit = {
>     val sc = ScioContext(args)
> 
>     sc.pubsubSubscription("streams-sub")
>       .map(parseStreamEvent)
>       .filter(_.duration > 30000) // > 30 sec
>       .groupByKey(_.userId)
>       .mapValues(calculateMetrics)
>       .saveAsBigQuery("streams.daily_metrics")
> 
>     sc.run()
>   }
> }
> ```
> 
> **Benefits:**
> - Type-safe Scala API
> - Same code for batch and streaming
> - BigQuery, Bigtable, Pub/Sub integration
> - Functional programming style
```

### 3. Luigi (Spotify Created - Legacy)

```
> **LUIGI HISTORY:**
> 
> * **Created:** 2012 (before Airflow)
> * **Status:** Still maintained, but Spotify uses Cloud Composer now
> 
> **Luigi (Python workflow framework) Example:**
> ```python
> class ProcessStreams(luigi.Task):
>     date = luigi.DateParameter()
> 
>     def requires(self):
>         return ExtractStreams(date=self.date)
> 
>     def output(self):
>         return luigi.LocalTarget(
>             f"/data/processed/{self.date}.parquet"
>         )
> 
>     def run(self):
>         # Processing logic
>         with self.output().open('w') as f:
>             f.write(processed_data)
> ```
> 
> **Key Concepts:**
> - Task = unit of work
> - Target = output (idempotency check)
> - Dependency resolution
> - Central scheduler
> 
> **Luigi vs Airflow:**
> - **Luigi:** Task-centric, simpler
> - **Airflow:** DAG-centric, more features
> - Both influenced by Spotify/Airbnb needs
```

### 4. Backstage (Developer Portal)

```
```mermaid
flowchart TD
    subgraph BACKSTAGE [" "]
        direction TB
        B_TITLE["BACKSTAGE<br>(Developer Portal Platform)"]
        style B_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        SC["Software Catalog<br>- All services, libraries, data pipelines<br>- Ownership information<br>- Dependencies graph<br>- Documentation links"]
        ST["Software Templates<br>- Create new services (scaffolding)<br>- Standard project structure<br>- CI/CD setup<br>- Best practices embedded"]
        TD["TechDocs<br>- Documentation as code<br>- Markdown in repo<br>- Rendered in Backstage"]
        PL["Plugins<br>- CI/CD status<br>- Cost tracking<br>- Data lineage<br>- API documentation"]
    end
```

> **BACKSTAGE ARCHITECTURE:**
> 
> * **Now:** CNCF Incubating Project
> * **Used by:** 2000+ companies
```

---

## 🎯 KEY DATA PRODUCTS

### 1. Discover Weekly (Personalized Playlist)

**WHAT - Mục tiêu:**
- Personalized music discovery for 600M+ users
- 30 new songs every Monday
- Balance familiarity với novelty
- Drive user engagement và retention

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph DISCOVER [" "]
        direction TB
        D_TITLE["DISCOVER WEEKLY<br>(30 songs every Monday)"]
        style D_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        S1["Step 1: User Taste Profile<br>- Listening history (weighted by recency)<br>- Skip patterns<br>- Saves and likes<br>- Playlist additions<br>=> User embedding vector"]
        
        S2["Step 2: Collaborative Filtering<br>Users who listen to similar tracks also listen to candidate tracks.<br>User A: [Track1, Track2, Track3, Track7]<br>User B: [Track1, Track2, Track4, Track8] (similar)<br>Recommend Track4, Track8 to User A"]
        
        S3["Step 3: Audio Analysis (Content-based)<br>Track Features:<br>- Tempo, key, mode<br>- Energy, danceability<br>- Acousticness, instrumentalness<br>- Deep learning audio embeddings<br>Find tracks with similar audio features"]
        
        S4["Step 4: NLP (Taste Analysis)<br>Analyze:<br>- Blog posts about artists<br>- News articles<br>- User reviews<br>=> Track cultural context embeddings"]
        
        S5["Step 5: Final Ranking<br>- Combine signals<br>- Filter already-heard tracks<br>- Ensure diversity (genres, artists)<br>- Novelty vs familiarity balance<br>=> 30 tracks for the week"]
        
        S1 --> S5
        S2 --> S5
        S3 --> S5
        S4 --> S5
    end
```

> **MODELS USED:**
> 
> 1. **Matrix Factorization:** User-item interactions, Implicit feedback (plays, skips)
> 2. **Deep Learning:** Audio CNN for feature extraction, Transformer for NLP
> 3. **Approximate Nearest Neighbor:** ANNOY (Spotify created), Fast similarity search at scale
```

**WHY - Lý do & Impact:**
- Most popular personalization feature
- Billions of streams from Discover Weekly alone
- Major differentiator vs competitors
- Drives Premium conversions

---

### 2. Spotify Wrapped

**WHAT - Mục tiêu:**
- Annual personalized listening summary
- Create shareable content for users
- Viral marketing (free PR)
- Celebrate user engagement

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph WRAPPED [" "]
        direction TB
        W_TITLE["SPOTIFY WRAPPED<br>(Annual listening summary)"]
        style W_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        DC["Data Collection (Year-round):<br>Stream events -> BigQuery<br>- Every play, skip, save<br>- Context (playlist, search, home)<br>- Duration played"]
        
        AGG["Aggregation (November):<br>Per-user aggregates:<br>- Top artists (by time)<br>- Top songs (by plays)<br>- Top genres<br>- Total minutes<br>- Listening personality<br>- Unique stats (e.g., 'top 0.1% listener')"]
        
        PRE["Pre-computation (December 1):<br>- Generate 600M+ personalized reports<br>- Store in Bigtable for fast access<br>- Pre-render some visualizations"]
        
        LAU["Launch Day:<br>- Massive traffic spike<br>- Bigtable handles read load<br>- Social sharing integration"]
        
        DC --> AGG
        AGG --> PRE
        PRE --> LAU
    end
```
```

**WHY - Lý do & Impact:**
- Billions of social media impressions
- Equivalent to $100M+ in advertising value
- Reinforces user identity with music
- Drives year-end engagement spike

---

### 3. Radio/Autoplay

**WHAT - Mục tiêu:**
- Continuous music experience
- Keep users engaged when content ends
- Discover related music naturally
- Maximize listening time

**HOW - Implementation:**

```
```mermaid
flowchart TD
    subgraph RADIO [" "]
        direction TB
        R_TITLE["RADIO ALGORITHM"]
        style R_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        START["User finishes playlist/album"]
        
        SS["Seed Selection<br>- Last played tracks<br>- Playlist theme<br>- User current mood (inferred)"]
        
        CG["Candidate Generation<br>- Similar tracks (audio features)<br>- Artist relations (graph)<br>- Collaborative filtering"]
        
        RR["Real-time Ranking<br>- User preferences<br>- Context (time, device)<br>- Variety constraints"]
        
        CA["Continuous Adaptation<br>- Track user actions (skips)<br>- Adjust on the fly<br>- Learn session preferences"]
        
        START --> SS
        SS --> CG
        CG --> RR
        RR --> CA
    end
```
```

### 4. Podcast Recommendations

```
```mermaid
flowchart TD
    subgraph PODCAST [" "]
        direction TB
        P_TITLE["PODCAST RECOMMENDATIONS"]
        style P_TITLE fill:none,stroke:none,font-weight:bold,color:#333
        
        CU["Content Understanding:<br>- Automatic Speech Recognition (ASR)<br>- Topic modeling from transcripts<br>- Episode embeddings<br>- Show-level features"]
        
        US["User Signals:<br>- Follow patterns<br>- Completion rates (listened to end?)<br>- Skip patterns<br>- Cross-media preferences (music -> podcasts)"]
    end
```

> **Challenges:**
> - Cold start (new podcasts)
> - Long-form content (1hr+ episodes)
> - Different consumption patterns vs music
> - Episode vs show recommendations
```

---

## 🛠️ SPOTIFY OPEN SOURCE CONTRIBUTIONS

```
> **SPOTIFY OSS ECOSYSTEM:**
> 
> * **Data Engineering:**
>   * Scio - Scala API for Apache Beam
>   * Luigi - Workflow management
>   * ANNOY - Approximate Nearest Neighbors
>   * Heroic - Time series database
> 
> * **Developer Experience:**
>   * Backstage - Developer portal (CNCF)
>   * Tingle - Push notification library
>   * Mobius - Reactive framework
> 
> * **Audio/ML:**
>   * Pedalboard - Audio effects library
>   * Basic-pitch - Audio-to-MIDI
>   * Klio - Audio ML pipelines
```

---

## 📊 SCALE & NUMBERS

```
> **SPOTIFY BY THE NUMBERS:**
> 
> * **Content:**
>   * 600M+ monthly active users
>   * 100M+ tracks
>   * 5M+ podcasts
>   * 4B+ playlists
> 
> * **Data:**
>   * Billions of stream events/day
>   * Petabytes in BigQuery
>   * Exabytes in GCS
>   * 1000s of ML models
> 
> * **Infrastructure:**
>   * 100s of microservices
>   * 10,000s of Dataflow jobs/day
>   * Multi-region GCP deployment
```

---

## 🔑 KEY LESSONS

### 1. Cloud-Native from Early Days
- GCP partnership since 2016
- Managed services reduce ops burden
- Focus on product, not infrastructure

### 2. Audio Features are Unique
- Deep learning on audio
- Content-based + collaborative filtering
- Audio analysis at petabyte scale

### 3. Developer Experience Matters
- Backstage created for internal use
- Now CNCF project
- Reduces cognitive load

### 4. Personalization at Scale
- Every user gets unique experience
- Balance exploration vs exploitation
- Context-aware recommendations

### 5. Real-time + Batch Hybrid
- Scio/Beam for unified processing
- Near-real-time for recommendations
- Batch for analytics and Wrapped

---

## 🔗 OPEN-SOURCE REPOS (Verified)

Spotify đóng góp nhiều tools cho cộng đồng, đặc biệt về developer experience:

| Repo | Stars | Mô Tả |
|------|-------|--------|
| [spotify/luigi](https://github.com/spotify/luigi) | 18.7k⭐ | Python batch pipeline framework — **Spotify tạo ra** (Erik Bernhardsson). Tiền bối của Airflow. |
| [backstage/backstage](https://github.com/backstage/backstage) | 29k⭐ | Developer portal platform — **Spotify tạo ra**, donated cho CNCF. |
| [spotify/scio](https://github.com/spotify/scio) | 2.5k⭐ | Scala API cho Apache Beam — **Spotify tạo ra** cho data processing. |

> 💡 **Hands-on:** `backstage/backstage` có hướng dẫn setup nhanh với `npx @backstage/create-app`. `spotify/luigi` dễ bắt đầu với `pip install luigi`.

---

## 📚 REFERENCES

**Engineering Blog:**
- Spotify Engineering: https://engineering.atspotify.com/

**Key Articles:**
- How Discover Weekly Works
- Backstage: https://backstage.io/
- Scio: https://spotify.github.io/scio/

**Talks:**
- Personalization at Spotify
- Building the World's Largest Music Catalog

---

*Document Version: 1.1*
*Last Updated: February 2026*
