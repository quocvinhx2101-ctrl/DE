# Serialization & Data Format Papers

## Những Paper Nền Tảng Về Serialization Formats và Data Encoding

---

## Mục Lục

1. [Apache Avro](#1-apache-avro---2009)
2. [Protocol Buffers](#2-protocol-buffers---2008)
3. [Apache Parquet](#3-apache-parquet---2013)
4. [Apache ORC](#4-apache-orc---2013)
5. [Apache Arrow](#5-apache-arrow---2016)
6. [FlatBuffers](#6-flatbuffers---2014)
7. [JSON / BSON / MessagePack](#7-json--bson--messagepack)
8. [Comparison Summary](#comparison-summary)
9. [Evolution and Trends](#evolution-and-trends)

---

## 1. APACHE AVRO - 2009

### Documentation Info
- **Title:** Apache Avro Specification
- **Authors:** Doug Cutting, et al. (Apache Foundation)
- **Source:** Apache Foundation
- **Link:** https://avro.apache.org/docs/current/specification/
- **Repo:** https://github.com/apache/avro

### Key Contributions
- Schema evolution with backward/forward compatibility
- Dynamic typing with schema resolution
- Compact binary encoding without field tags
- Built-in RPC framework
- Default serialization format for Kafka

### Avro Schema and Encoding

```mermaid
graph TD
    subgraph Schema[" "]
        Schema_title["Avro Schema (JSON)"]
        style Schema_title fill:none,stroke:none,color:#333,font-weight:bold
        S1["type: record<br/>name: User<br/>namespace: com.example"]
        S2["fields:<br/>  id: long<br/>  name: string<br/>  email: union(null, string)<br/>  age: int, default=0"]
    end

    subgraph Encoding[" "]
        Encoding_title["Binary Encoding"]
        style Encoding_title fill:none,stroke:none,color:#333,font-weight:bold
        E1["No field names in data!<br/>No field tags!<br/>Schema required at read/write"]
        E2["id → varint (zigzag)<br/>name → length + UTF-8<br/>email → union index + value<br/>age → varint (zigzag)"]
    end

    subgraph File[" "]
        File_title["Avro File Format (.avro)"]
        style File_title fill:none,stroke:none,color:#333,font-weight:bold
        F1["File Header<br/>Magic: Obj1<br/>Metadata (schema, codec)<br/>Sync marker (16 bytes)"]
        F2["Data Block 1<br/>Object count<br/>Compressed size<br/>Data (codec compressed)<br/>Sync marker"]
        F3["Data Block 2<br/>..."]
    end

    Schema --> Encoding --> File

    style Schema fill:#e3f2fd
    style Encoding fill:#e8f5e9
    style File fill:#fff3e0
```

### Schema Evolution

```mermaid
graph TD
    subgraph Evolution[" "]
        Evolution_title["Schema Evolution Rules"]
        style Evolution_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Backward[" "]
            Backward_title["Backward Compatible<br/>New reader, old data ✅"]
            style Backward_title fill:none,stroke:none,color:#333,font-weight:bold
            BC1["Add field WITH default"]
            BC2["Remove field WITH default"]
        end

        subgraph Forward[" "]
            Forward_title["Forward Compatible<br/>Old reader, new data ✅"]
            style Forward_title fill:none,stroke:none,color:#333,font-weight:bold
            FC1["Remove field WITH default"]
            FC2["Add field WITH default"]
        end

        subgraph Full[" "]
            Full_title["Full Compatible<br/>Both directions ✅"]
            style Full_title fill:none,stroke:none,color:#333,font-weight:bold
            FULL1["Add/remove fields<br/>only WITH defaults"]
        end

        subgraph Breaking[" "]
            Breaking_title["Breaking Changes ❌"]
            style Breaking_title fill:none,stroke:none,color:#333,font-weight:bold
            BK1["Change field type"]
            BK2["Rename field"]
            BK3["Remove field without default"]
            BK4["Add field without default"]
        end
    end

    style Backward fill:#e8f5e9
    style Forward fill:#e3f2fd
    style Full fill:#c8e6c9
    style Breaking fill:#ffcdd2
```

### Schema Resolution

```mermaid
sequenceDiagram
    participant Writer as Writer (V1 Schema)
    participant Data as Avro Data
    participant Reader as Reader (V2 Schema)

    Note over Writer: Schema V1:<br/>{id: long, name: string}
    Writer->>Data: Write with V1 schema

    Note over Reader: Schema V2:<br/>{id: long, name: string,<br/>email: string, default: null}
    Reader->>Data: Read with V2 schema

    Note over Reader: Schema Resolution:<br/>id: read from data ✅<br/>name: read from data ✅<br/>email: not in data → use default null ✅
```

### Schema Registry Pattern

```mermaid
graph TD
    subgraph Producers[" "]
        Producers_title["Producers"]
        style Producers_title fill:none,stroke:none,color:#333,font-weight:bold
        P1[Producer A<br/>Schema V1]
        P2[Producer B<br/>Schema V2]
    end

    subgraph Registry[" "]
        Registry_title["Schema Registry"]
        style Registry_title fill:none,stroke:none,color:#333,font-weight:bold
        SR[Confluent Schema Registry<br/>or AWS Glue Schema Registry]
        SV["Schemas stored:<br/>ID 1 → V1 schema<br/>ID 2 → V2 schema"]
        Compat["Compatibility Check<br/>BACKWARD, FORWARD,<br/>FULL, NONE"]
    end

    subgraph Kafka[" "]
        Kafka_title["Kafka"]
        style Kafka_title fill:none,stroke:none,color:#333,font-weight:bold
        Topic[Topic: user-events]
        Msg["Message format:<br/>[Magic byte][Schema ID 4B][Avro data]"]
    end

    subgraph Consumers[" "]
        Consumers_title["Consumers"]
        style Consumers_title fill:none,stroke:none,color:#333,font-weight:bold
        C1[Consumer X<br/>Reads with V1]
        C2[Consumer Y<br/>Reads with V2]
    end

    P1 -->|"1. Register schema"| SR
    P1 -->|"2. Write data"| Topic
    P2 -->|"1. Register schema"| SR
    P2 -->|"2. Write data"| Topic
    Topic --> C1
    Topic --> C2
    C1 -->|"3. Fetch schema by ID"| SR
    C2 -->|"3. Fetch schema by ID"| SR

    style Registry fill:#e8f5e9
    style Kafka fill:#e3f2fd
```

### Impact on Modern Systems
- **Apache Kafka** — Default serialization with Schema Registry
- **Apache Spark** — Native Avro support
- **Hadoop ecosystem** — Standard file format
- **Data pipelines** — Schema evolution for streaming

---

## 2. PROTOCOL BUFFERS - 2008

### Paper/Documentation Info
- **Title:** Protocol Buffers
- **Authors:** Google (Kenton Varda, et al.)
- **Source:** Google Developers
- **Link:** https://protobuf.dev/
- **Spec:** https://protobuf.dev/programming-guides/encoding/
- **GitHub:** https://github.com/protocolbuffers/protobuf

### Key Contributions
- Efficient binary encoding with field numbering
- Strong typing with code generation
- Backward/forward compatible evolution
- Foundation for gRPC
- Google's internal standard for all data exchange

### Protobuf Schema and Encoding

```mermaid
graph TD
    subgraph ProtoSchema[" "]
        ProtoSchema_title[".proto Schema"]
        style ProtoSchema_title fill:none,stroke:none,color:#333,font-weight:bold
        PS["syntax = 'proto3'<br/><br/>message User {<br/>  int64 id = 1;<br/>  string name = 2;<br/>  optional string email = 3;<br/>  int32 age = 4;<br/>  repeated string tags = 5;<br/>}"]
    end

    subgraph WireFormat[" "]
        WireFormat_title["Wire Format"]
        style WireFormat_title fill:none,stroke:none,color:#333,font-weight:bold
        WF["Each field:<br/>[tag][data]<br/><br/>tag = (field_number << 3) | wire_type<br/><br/>Wire types:<br/>0 = Varint (int, bool, enum)<br/>1 = 64-bit (fixed64, double)<br/>2 = Length-delimited (string, bytes)<br/>5 = 32-bit (fixed32, float)"]
    end

    subgraph Varint[" "]
        Varint_title["Varint Encoding"]
        style Varint_title fill:none,stroke:none,color:#333,font-weight:bold
        VI["150 = 10010110₂<br/>Split into 7-bit groups:<br/>0000001 | 0010110<br/>Set MSB for continuation:<br/>10010110 00000001<br/>= 0x96 0x01"]
    end

    ProtoSchema --> WireFormat --> Varint

    style ProtoSchema fill:#e3f2fd
    style WireFormat fill:#e8f5e9
    style Varint fill:#fff3e0
```

### Protobuf vs Avro

```mermaid
graph TD
    subgraph Protobuf[" "]
        Protobuf_title["Protocol Buffers"]
        style Protobuf_title fill:none,stroke:none,color:#333,font-weight:bold
        PB1["Field identified by NUMBER<br/>id = 1, name = 2"]
        PB2["Tags in data → self-describing<br/>Unknown fields skipped"]
        PB3["Code generation REQUIRED<br/>Compile .proto to code"]
        PB4["Best for: RPC, microservices"]
    end

    subgraph Avro[" "]
        Avro_title["Apache Avro"]
        style Avro_title fill:none,stroke:none,color:#333,font-weight:bold
        AV1["Field identified by POSITION<br/>Schema required at read/write"]
        AV2["No tags → more compact<br/>Schema in file header"]
        AV3["Code generation OPTIONAL<br/>Dynamic typing supported"]
        AV4["Best for: Kafka, data storage"]
    end

    style Protobuf fill:#e3f2fd
    style Avro fill:#e8f5e9
```

### Evolution Rules

```mermaid
graph TD
    subgraph Safe[" "]
        Safe_title["Safe Changes ✅"]
        style Safe_title fill:none,stroke:none,color:#333,font-weight:bold
        S1["Add new field (new number)"]
        S2["Remove field (reserve number!)"]
        S3["int32 ↔ int64 ↔ uint32 ↔ uint64 ↔ bool"]
        S4["string ↔ bytes (if valid UTF-8)"]
    end

    subgraph Unsafe[" "]
        Unsafe_title["Unsafe Changes ❌"]
        style Unsafe_title fill:none,stroke:none,color:#333,font-weight:bold
        U1["Change field number"]
        U2["Change wire type<br/>(e.g., int → string)"]
        U3["Reuse reserved field number"]
    end

    subgraph BestPractice[" "]
        BestPractice_title["Best Practices"]
        style BestPractice_title fill:none,stroke:none,color:#333,font-weight:bold
        BP1["Always reserve removed field numbers<br/>reserved 3, 7, 9;"]
        BP2["Use optional for new fields"]
        BP3["Never change field semantics"]
    end

    style Safe fill:#e8f5e9
    style Unsafe fill:#ffcdd2
    style BestPractice fill:#e3f2fd
```

### Impact on Modern Systems
- **gRPC** — Built on Protobuf for RPC
- **Google services** — Internal standard (Stubby → gRPC)
- **Microservices** — Common choice for service-to-service
- **Buf** — Modern Protobuf tooling (linting, breaking change detection)

---

## 3. APACHE PARQUET - 2013

### Paper/Documentation Info
- **Title:** Apache Parquet
- **Authors:** Julien Le Dem (Twitter), Nong Li (Cloudera), et al.
- **Source:** Apache Foundation
- **Link:** https://parquet.apache.org/docs/
- **Format Spec:** https://github.com/apache/parquet-format
- **GitHub:** https://github.com/apache/parquet-java

### Key Contributions
- Columnar storage format for analytics
- Nested data support via Dremel encoding
- Efficient compression per column
- Predicate pushdown via statistics
- THE standard format for data lakes

### Parquet File Structure

```mermaid
graph TD
    subgraph ParquetFile[" "]
        ParquetFile_title["Parquet File"]
        style ParquetFile_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph RG1[" "]
            RG1_title["Row Group 1 (typically 128MB)"]
            style RG1_title fill:none,stroke:none,color:#333,font-weight:bold
            subgraph CC_A[" "]
                CC_A_title["Column A Chunk"]
                style CC_A_title fill:none,stroke:none,color:#333,font-weight:bold
                PA1[Data Page 1]
                PA2[Data Page 2]
                PA3[Dictionary Page]
            end
            subgraph CC_B[" "]
                CC_B_title["Column B Chunk"]
                style CC_B_title fill:none,stroke:none,color:#333,font-weight:bold
                PB1[Data Page 1]
            end
            subgraph CC_C[" "]
                CC_C_title["Column C Chunk"]
                style CC_C_title fill:none,stroke:none,color:#333,font-weight:bold
                PC1[Data Page 1]
                PC2[Data Page 2]
            end
        end

        subgraph RG2[" "]
            RG2_title["Row Group 2"]
            style RG2_title fill:none,stroke:none,color:#333,font-weight:bold
            RG2D["... more column chunks"]
        end

        subgraph Footer[" "]
            Footer_title["File Footer"]
            style Footer_title fill:none,stroke:none,color:#333,font-weight:bold
            Schema_F["Schema<br/>(column names, types, nesting)"]
            RGMeta["Row Group Metadata<br/>(offsets, sizes)"]
            ColStats["Column Statistics<br/>(min, max, null_count per chunk)"]
        end

        Magic["Magic: PAR1"]
    end

    style RG1 fill:#e3f2fd
    style RG2 fill:#e3f2fd
    style Footer fill:#e8f5e9
```

### Dremel Encoding (Nested Data)

```mermaid
graph TD
    subgraph Dremel[" "]
        Dremel_title["Dremel Encoding for Nested Data"]
        style Dremel_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Schema_D[" "]
            Schema_D_title["Schema"]
            style Schema_D_title fill:none,stroke:none,color:#333,font-weight:bold
            SD["message Document {<br/>  repeated group Name {<br/>    repeated group Language {<br/>      required string Code;<br/>    }<br/>  }<br/>}"]
        end

        subgraph Data_D[" "]
            Data_D_title["Data"]
            style Data_D_title fill:none,stroke:none,color:#333,font-weight:bold
            DD["Document {<br/>  Name: [<br/>    {Language: [{Code:'en'},{Code:'fr'}]},<br/>    {Language: []}<br/>  ]<br/>}"]
        end

        subgraph Encoded[" "]
            Encoded_title["Encoded Columns"]
            style Encoded_title fill:none,stroke:none,color:#333,font-weight:bold
            EC["Code  | R | D<br/>'en'  | 0 | 3<br/>'fr'  | 1 | 3<br/>null  | 1 | 1<br/><br/>R = Repetition level<br/>(which repeated field starts new)<br/>D = Definition level<br/>(how many optional fields defined)"]
        end
    end

    Schema_D --> Data_D --> Encoded

    style Schema_D fill:#e3f2fd
    style Data_D fill:#e8f5e9
    style Encoded fill:#fff3e0
```

### Predicate Pushdown

```mermaid
flowchart TD
    Query["Query: WHERE age > 30 AND city = 'NYC'"]

    subgraph FileLevel[" "]
        FileLevel_title["File-Level Skipping"]
        style FileLevel_title fill:none,stroke:none,color:#333,font-weight:bold
        FL1["Check file footer statistics"]
        FL2["File min/max for 'age'"]
    end

    subgraph RGLevel[" "]
        RGLevel_title["Row Group Skipping"]
        style RGLevel_title fill:none,stroke:none,color:#333,font-weight:bold
        RG1S["RG1: age min=18, max=25<br/>❌ SKIP (max < 30)"]
        RG2S["RG2: age min=22, max=45<br/>✅ READ (range overlaps)"]
        RG3S["RG3: age min=35, max=60<br/>✅ READ"]
    end

    subgraph PageLevel[" "]
        PageLevel_title["Page-Level Skipping (v2)"]
        style PageLevel_title fill:none,stroke:none,color:#333,font-weight:bold
        PG1["Page 1: age min=22, max=28<br/>❌ SKIP"]
        PG2["Page 2: age min=30, max=45<br/>✅ READ"]
    end

    subgraph BloomFilter[" "]
        BloomFilter_title["Bloom Filter"]
        style BloomFilter_title fill:none,stroke:none,color:#333,font-weight:bold
        BF["city bloom filter:<br/>'NYC' → probably present ✅<br/>'XYZ' → definitely absent ❌"]
    end

    Query --> FileLevel --> RGLevel --> PageLevel --> BloomFilter

    style RG1S fill:#ffebee
    style RG2S fill:#e8f5e9
    style RG3S fill:#e8f5e9
    style PG1 fill:#ffebee
    style PG2 fill:#e8f5e9
```

### Parquet Encodings

```mermaid
graph TD
    subgraph Encodings[" "]
        Encodings_title["Parquet Encodings"]
        style Encodings_title fill:none,stroke:none,color:#333,font-weight:bold
        Plain["PLAIN<br/>Raw values<br/>Simple, no overhead"]
        Dict["DICTIONARY<br/>Unique values + indices<br/>Great for low cardinality"]
        RLE["RLE_DICTIONARY<br/>Run-length encoded indices<br/>Best for sorted/repeated"]
        Delta["DELTA_BINARY_PACKED<br/>Store deltas between values<br/>Great for timestamps, IDs"]
        DeltaStr["DELTA_LENGTH_BYTE_ARRAY<br/>Delta-encoded string lengths<br/>Good for similar strings"]
        ByteSplit["BYTE_STREAM_SPLIT<br/>Split float bytes<br/>Better compression for floats"]
    end

    style Plain fill:#e3f2fd
    style Dict fill:#e8f5e9
    style RLE fill:#fff3e0
    style Delta fill:#f3e5f5
    style DeltaStr fill:#fce4ec
    style ByteSplit fill:#e3f2fd
```

### Compression Options

| Codec | Speed | Ratio | Best For | Used By |
|-------|-------|-------|----------|---------|
| SNAPPY | ⚡⚡⚡ Fast | Medium | Real-time analytics | Spark default |
| GZIP | ⚡ Slow | High | Storage optimization | Cold storage |
| LZ4 | ⚡⚡⚡⚡ Fastest | Low-Medium | Hot data | Real-time |
| ZSTD | ⚡⚡ Balanced | High | General purpose | Modern default |
| BROTLI | ⚡ Slowest | Highest | Maximum compression | Archival |

### Impact on Modern Systems
- **Data Lakes** — THE dominant storage format
- **Spark, Hive, Presto/Trino** — Standard analytics format
- **Table formats** — Iceberg, Delta Lake, Hudi all use Parquet
- **DuckDB, Polars** — Native Parquet support
- **Pandas/PyArrow** — Default columnar file format

---

## 4. APACHE ORC - 2013

### Paper/Documentation Info
- **Title:** Apache ORC (Optimized Row Columnar)
- **Authors:** Owen O'Malley, et al. (Hortonworks)
- **Source:** Apache Foundation
- **Link:** https://orc.apache.org/
- **Spec:** https://orc.apache.org/specification/
- **GitHub:** https://github.com/apache/orc

### Key Contributions
- Optimized columnar format for Hive
- Built-in lightweight indexes (min/max per stripe, row group)
- ACID transaction support for Hive
- Bloom filters for efficient lookups

### ORC File Structure

```mermaid
graph TD
    subgraph ORCFile[" "]
        ORCFile_title["ORC File"]
        style ORCFile_title fill:none,stroke:none,color:#333,font-weight:bold
        Header["Header: 'ORC'"]

        subgraph Stripe1[" "]
            Stripe1_title["Stripe 1 (64-256 MB)"]
            style Stripe1_title fill:none,stroke:none,color:#333,font-weight:bold
            subgraph IndexData[" "]
                IndexData_title["Index Data"]
                style IndexData_title fill:none,stroke:none,color:#333,font-weight:bold
                ID1["Row Group Index<br/>Min/max per 10K rows"]
                ID2["Bloom Filters<br/>Per column"]
            end

            subgraph RowData[" "]
                RowData_title["Row Data"]
                style RowData_title fill:none,stroke:none,color:#333,font-weight:bold
                RD1["Column Streams<br/>Present (null bitmap)<br/>Data (values)<br/>Length (var-length)<br/>Secondary (nanos)"]
            end

            StripeFooter["Stripe Footer<br/>Encoding info<br/>Stream descriptions"]
        end

        Stripe2["Stripe 2<br/>..."]

        subgraph FileFooter[" "]
            FileFooter_title["File Footer"]
            style FileFooter_title fill:none,stroke:none,color:#333,font-weight:bold
            FF1["Schema definition"]
            FF2["Stripe metadata<br/>Offset, length, row count"]
            FF3["Column statistics<br/>Min, max, count, sum"]
        end

        Postscript["Postscript<br/>Compression codec<br/>Footer length"]
    end

    style Stripe1 fill:#e3f2fd
    style IndexData fill:#e8f5e9
    style RowData fill:#fff3e0
    style FileFooter fill:#f3e5f5
```

### ORC vs Parquet

```mermaid
graph TD
    subgraph Comparison[" "]
        Comparison_title["ORC vs Parquet"]
        style Comparison_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph ORC_Side[" "]
            ORC_Side_title["ORC Strengths"]
            style ORC_Side_title fill:none,stroke:none,color:#333,font-weight:bold
            O1["Built-in indexes<br/>(row group level)"]
            O2["Native ACID support<br/>(Hive transactions)"]
            O3["Better integer encoding<br/>(Patched Base, Delta)"]
            O4["Stripe-level statistics"]
            O5["Optimized for Hive"]
        end

        subgraph Parquet_Side[" "]
            Parquet_Side_title["Parquet Strengths"]
            style Parquet_Side_title fill:none,stroke:none,color:#333,font-weight:bold
            P1["Better nested data<br/>(Dremel encoding)"]
            P2["Wider ecosystem<br/>(Spark, Presto, Arrow)"]
            P3["More compression options<br/>(ZSTD, Brotli, LZ4)"]
            P4["Column-level Bloom filters"]
            P5["Industry standard"]
        end
    end

    style ORC_Side fill:#e3f2fd
    style Parquet_Side fill:#e8f5e9
```

### ORC ACID Support

```mermaid
flowchart LR
    subgraph ACID[" "]
        ACID_title["ORC ACID for Hive"]
        style ACID_title fill:none,stroke:none,color:#333,font-weight:bold
        Base["Base File<br/>Original data<br/>(full snapshot)"]
        Delta1["Delta File 1<br/>INSERT records"]
        Delta2["Delta File 2<br/>UPDATE records"]
        Delete1["Delete File 1<br/>DELETE markers"]
    end

    subgraph Read[" "]
        Read_title["Read Path"]
        style Read_title fill:none,stroke:none,color:#333,font-weight:bold
        Merge["Merge on Read<br/>Base + Deltas - Deletes<br/>= Current state"]
    end

    subgraph Compact[" "]
        Compact_title["Compaction"]
        style Compact_title fill:none,stroke:none,color:#333,font-weight:bold
        Minor["Minor Compaction<br/>Merge delta files"]
        Major["Major Compaction<br/>Merge everything into<br/>new base file"]
    end

    Base --> Read
    Delta1 --> Read
    Delta2 --> Read
    Delete1 --> Read
    Read --> Compact

    style ACID fill:#e3f2fd
    style Read fill:#e8f5e9
    style Compact fill:#fff3e0
```

### Impact on Modern Systems
- **Apache Hive** — Primary format, ACID support
- **Presto/Trino** — Supported format
- **Apache Spark** — Supported format
- **Declining usage** — Parquet becoming more dominant

---

## 5. APACHE ARROW - 2016

### Paper/Documentation Info
- **Title:** Apache Arrow: A Cross-Language Development Platform for In-Memory Analytics
- **Authors:** Wes McKinney, Jacques Nadeau, et al.
- **Source:** Apache Foundation
- **Link:** https://arrow.apache.org/
- **Format Spec:** https://arrow.apache.org/docs/format/Columnar.html
- **GitHub:** https://github.com/apache/arrow

### Key Contributions
- Standardized in-memory columnar format
- Zero-copy data sharing across languages
- SIMD-friendly memory layout
- Cross-language interoperability (C++, Python, Java, Rust, Go, etc.)
- Foundation for modern analytics engines

### Arrow Memory Layout

```mermaid
graph TD
    subgraph Primitive[" "]
        Primitive_title["Primitive Array (int64)"]
        style Primitive_title fill:none,stroke:none,color:#333,font-weight:bold
        P_Valid["Validity Bitmap<br/>[1, 1, 0, 1] → bit per value"]
        P_Data["Data Buffer<br/>[100, 200, _, 400]<br/>64-bit aligned, contiguous"]
    end

    subgraph VarLen[" "]
        VarLen_title["Variable-Length Array (string)"]
        style VarLen_title fill:none,stroke:none,color:#333,font-weight:bold
        V_Valid["Validity Bitmap<br/>[1, 1, 1, 0]"]
        V_Offsets["Offsets Buffer (int32)<br/>[0, 5, 9, 14, 14]"]
        V_Data["Data Buffer<br/>'H e l l o J o h n A l i c e'"]
        V_Note["String 0: data[0:5] = 'Hello'<br/>String 1: data[5:9] = 'John'<br/>String 2: data[9:14] = 'Alice'<br/>String 3: null (offsets equal)"]
    end

    subgraph Nested[" "]
        Nested_title["Nested Array: List<int32>"]
        style Nested_title fill:none,stroke:none,color:#333,font-weight:bold
        N_Offsets["Offsets [0, 3, 3, 5]"]
        N_Child["Child Array: [1, 2, 3, 4, 5]"]
        N_Note["List 0: [1, 2, 3]<br/>List 1: [] (empty)<br/>List 2: [4, 5]"]
    end

    style Primitive fill:#e3f2fd
    style VarLen fill:#e8f5e9
    style Nested fill:#fff3e0
```

### Zero-Copy Across Languages

```mermaid
graph LR
    subgraph Process[" "]
        Process_title["Same Process Memory"]
        style Process_title fill:none,stroke:none,color:#333,font-weight:bold
        Memory["Arrow Memory<br/>(shared buffer)"]
    end

    Python["Python<br/>PyArrow"] -->|"pointer"| Memory
    R["R<br/>arrow package"] -->|"pointer"| Memory
    Java["Java<br/>Arrow Java"] -->|"pointer"| Memory
    Rust["Rust<br/>arrow-rs"] -->|"pointer"| Memory

    Note["No serialization!<br/>No copying!<br/>Same memory layout<br/>across all languages"]

    style Process fill:#e8f5e9
```

### Arrow Flight

```mermaid
graph TD
    subgraph Flight[" "]
        Flight_title["Arrow Flight Protocol"]
        style Flight_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Client[" "]
            Client_title["Client"]
            style Client_title fill:none,stroke:none,color:#333,font-weight:bold
            C1[GetFlightInfo<br/>Query metadata]
            C2[DoGet<br/>Stream data FROM server]
            C3[DoPut<br/>Stream data TO server]
            C4[DoExchange<br/>Bidirectional streaming]
        end

        subgraph Transport[" "]
            Transport_title["Transport"]
            style Transport_title fill:none,stroke:none,color:#333,font-weight:bold
            gRPC[gRPC + Arrow IPC<br/>High-performance<br/>binary streaming]
        end

        subgraph Server[" "]
            Server_title["Server"]
            style Server_title fill:none,stroke:none,color:#333,font-weight:bold
            S1[Flight Server<br/>Serves Arrow data]
            S2[Multiple endpoints<br/>Parallel streams]
        end

        Client <-->|"Arrow IPC batches<br/>over gRPC"| Transport <--> Server
    end

    subgraph Perf[" "]
        Perf_title["Performance"]
        style Perf_title fill:none,stroke:none,color:#333,font-weight:bold
        PF["10-100× faster than JDBC/ODBC<br/>No serialization overhead<br/>Columnar streaming<br/>Parallel endpoints"]
    end

    style Flight fill:#e3f2fd
    style Perf fill:#e8f5e9
```

### Arrow IPC Formats

```mermaid
graph TD
    subgraph Stream[" "]
        Stream_title["IPC Stream Format"]
        style Stream_title fill:none,stroke:none,color:#333,font-weight:bold
        SS["Schema message"]
        SB1["RecordBatch 1"]
        SB2["RecordBatch 2"]
        SB3["..."]
        SE["End of stream"]
        SS --> SB1 --> SB2 --> SB3 --> SE
    end

    subgraph File[" "]
        File_title["IPC File Format"]
        style File_title fill:none,stroke:none,color:#333,font-weight:bold
        FM1["ARROW1 (magic)"]
        FS["Schema"]
        FB1["RecordBatch 1"]
        FB2["RecordBatch 2"]
        FF["Footer<br/>(offsets to batches)"]
        FM2["ARROW1 (magic)"]
        FM1 --> FS --> FB1 --> FB2 --> FF --> FM2
    end

    style Stream fill:#e3f2fd
    style File fill:#e8f5e9
```

### Impact on Modern Systems
- **Pandas 2.0** — Arrow backend (PyArrow)
- **DuckDB** — Native Arrow integration
- **Polars** — Built on Arrow (arrow-rs)
- **DataFusion** — Arrow-native query engine
- **Spark** — Arrow for pandas UDFs
- **Flink** — Arrow for Python UDFs
- **Snowflake, Databricks** — Arrow Flight for data transfer

---

## 6. FLATBUFFERS - 2014

### Documentation Info
- **Title:** FlatBuffers
- **Authors:** Wouter van Oortmerssen (Google)
- **Source:** Google
- **Link:** https://google.github.io/flatbuffers/
- **GitHub:** https://github.com/google/flatbuffers

### Key Contributions
- Zero-copy access to serialized data (no parsing!)
- Memory-mapped file friendly
- Random access to any field
- Optimized for game engines and mobile

### FlatBuffers vs Protobuf

```mermaid
graph TD
    subgraph Protobuf_Flow[" "]
        Protobuf_Flow_title["Protobuf Access"]
        style Protobuf_Flow_title fill:none,stroke:none,color:#333,font-weight:bold
        PB_Recv["Receive binary data"]
        PB_Parse["Parse (deserialize)<br/>Allocate objects<br/>Copy data"]
        PB_Access["Access fields<br/>Through objects"]
        PB_Recv --> PB_Parse --> PB_Access
        PB_Note["⚠️ Parse overhead<br/>⚠️ Memory allocation<br/>⚠️ CPU + memory cost"]
    end

    subgraph FB_Flow[" "]
        FB_Flow_title["FlatBuffers Access"]
        style FB_Flow_title fill:none,stroke:none,color:#333,font-weight:bold
        FB_Recv["Receive binary buffer"]
        FB_Access["Access fields directly<br/>Pointer arithmetic only<br/>No parsing, no copying!"]
        FB_Recv --> FB_Access
        FB_Note["✅ Zero-copy<br/>✅ No allocation<br/>✅ Instant access"]
    end

    style Protobuf_Flow fill:#fff3e0
    style FB_Flow fill:#e8f5e9
```

### Buffer Layout

```mermaid
graph TD
    subgraph Layout[" "]
        Layout_title["FlatBuffers Binary Layout"]
        style Layout_title fill:none,stroke:none,color:#333,font-weight:bold
        Root["Root Table Offset<br/>(4 bytes, points to main table)"]
        VTable["VTable<br/>vtable_size | table_size |<br/>field_0_offset | field_1_offset | ..."]
        Table["Table<br/>soffset_to_vtable |<br/>field values (inline or offset)"]
        Strings["Strings / Vectors<br/>length (4B) | data bytes"]
    end

    Root -->|"offset"| Table
    Table -->|"soffset"| VTable
    Table -->|"offset"| Strings

    style Root fill:#e3f2fd
    style VTable fill:#e8f5e9
    style Table fill:#fff3e0
    style Strings fill:#f3e5f5
```

### Use Cases

| Use Case | Why FlatBuffers? |
|----------|-----------------|
| Game engines | Real-time, zero-copy, memory constraints |
| Mobile apps | Battery efficiency, fast startup |
| Network protocols | Low-latency, no parsing overhead |
| Memory-mapped files | Direct access, no deserialization |
| IoT / Embedded | Minimal CPU and memory requirements |

---

## 7. JSON / BSON / MESSAGEPACK

### Documentation Info
- **JSON:** https://www.json.org/ (RFC 8259)
- **BSON:** https://bsonspec.org/
- **MessagePack:** https://msgpack.org/

### Format Comparison

```mermaid
graph TD
    subgraph JSON_F[" "]
        JSON_F_title["JSON"]
        style JSON_F_title fill:none,stroke:none,color:#333,font-weight:bold
        J1["Human readable ✅"]
        J2["Self-describing ✅"]
        J3["Verbose ❌ (field names repeated)"]
        J4["No binary data ❌ (base64 needed)"]
        J5["Universal support ✅"]
    end

    subgraph BSON_F[" "]
        BSON_F_title["BSON (Binary JSON)"]
        style BSON_F_title fill:none,stroke:none,color:#333,font-weight:bold
        B1["Binary format"]
        B2["Additional types (Date, Binary, ObjectId)"]
        B3["Used by MongoDB"]
        B4["Slightly larger than JSON!"]
        B5["Fast traversal (length-prefixed)"]
    end

    subgraph MsgPack_F[" "]
        MsgPack_F_title["MessagePack"]
        style MsgPack_F_title fill:none,stroke:none,color:#333,font-weight:bold
        M1["Binary JSON (compact)"]
        M2["25-50% smaller than JSON"]
        M3["Fast serialization"]
        M4["Wide language support"]
        M5["Used in: Redis, Fluentd"]
    end

    style JSON_F fill:#e3f2fd
    style BSON_F fill:#e8f5e9
    style MsgPack_F fill:#fff3e0
```

### Size Comparison

```mermaid
graph LR
    subgraph Sizes[" "]
        Sizes_title["Size Comparison for Same Data"]
        style Sizes_title fill:none,stroke:none,color:#333,font-weight:bold
        JSON_S["JSON<br/>46 bytes"]
        BSON_S["BSON<br/>45 bytes"]
        MsgPack_S["MessagePack<br/>25 bytes"]
        Protobuf_S["Protobuf<br/>12 bytes"]
        Avro_S["Avro<br/>10 bytes"]
    end

    JSON_S -.->|"similar"| BSON_S
    BSON_S -.->|"-45%"| MsgPack_S
    MsgPack_S -.->|"-52%"| Protobuf_S
    Protobuf_S -.->|"-17%"| Avro_S

    style JSON_S fill:#ffcdd2
    style BSON_S fill:#fff3e0
    style MsgPack_S fill:#e3f2fd
    style Protobuf_S fill:#e8f5e9
    style Avro_S fill:#c8e6c9
```

### When to Use What

```mermaid
graph TD
    Start{What's your use case?}

    Start -->|"Human readable<br/>config, REST API"| JSON_Use["Use JSON<br/>Universal, debuggable"]
    Start -->|"MongoDB"| BSON_Use["Use BSON<br/>Native MongoDB format"]
    Start -->|"Compact JSON<br/>logs, caching"| MP_Use["Use MessagePack<br/>Fast, smaller, flexible"]
    Start -->|"RPC, microservices"| PB_Use["Use Protobuf + gRPC<br/>Strong typing, fast"]
    Start -->|"Kafka, streaming"| AV_Use["Use Avro<br/>Schema evolution, compact"]
    Start -->|"Analytics storage"| PQ_Use["Use Parquet<br/>Columnar, compressed"]
    Start -->|"In-memory analytics"| AR_Use["Use Arrow<br/>Zero-copy, cross-language"]
    Start -->|"Game engine, mobile"| FB_Use["Use FlatBuffers<br/>Zero-copy, instant access"]

    style JSON_Use fill:#e3f2fd
    style BSON_Use fill:#e8f5e9
    style MP_Use fill:#fff3e0
    style PB_Use fill:#f3e5f5
    style AV_Use fill:#fce4ec
    style PQ_Use fill:#e3f2fd
    style AR_Use fill:#e8f5e9
    style FB_Use fill:#fff3e0
```

---

## COMPARISON SUMMARY

### Format Feature Matrix

```mermaid
graph TD
    subgraph Matrix[" "]
        Matrix_title["Feature Comparison"]
        style Matrix_title fill:none,stroke:none,color:#333,font-weight:bold
        subgraph Row[" "]
            Row_title["Row-Oriented"]
            style Row_title fill:none,stroke:none,color:#333,font-weight:bold
            JSON2["JSON: Human readable, verbose"]
            Avro2["Avro: Schema evolution, Kafka"]
            PB2["Protobuf: Compact, typed, gRPC"]
            FB2["FlatBuffers: Zero-copy access"]
            MP2["MessagePack: Binary JSON"]
        end

        subgraph Col[" "]
            Col_title["Column-Oriented"]
            style Col_title fill:none,stroke:none,color:#333,font-weight:bold
            Parquet2["Parquet: Analytics storage king"]
            ORC2["ORC: Hive-optimized, ACID"]
            Arrow2["Arrow: In-memory standard"]
        end
    end

    style Row fill:#e3f2fd
    style Col fill:#e8f5e9
```

### Comprehensive Comparison Table

| Feature | JSON | MsgPack | Avro | Protobuf | FlatBuffers | Parquet | ORC | Arrow |
|---------|------|---------|------|----------|-------------|---------|-----|-------|
| Schema | ❌ No | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Self-describing | ✅ | ✅ | ❌ | Partial | ❌ | Partial | Partial | ✅ |
| Compactness | Poor | Good | Great | Great | Good | Best | Best | Good |
| Zero-copy | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Columnar | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Schema evolution | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Compression | External | ❌ | Per-file | External | ❌ | Per-column | Per-stripe | ❌ |
| Nested data | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Dremel) | ✅ | ✅ |

### Use Case Mapping

| Use Case | Best Format | Why |
|----------|-------------|-----|
| Config files | JSON, YAML | Human readable |
| REST APIs | JSON | Universal support |
| gRPC services | Protobuf | Strong typing, fast |
| Kafka messages | Avro | Schema evolution |
| Analytics storage | Parquet | Columnar, compressed |
| In-memory compute | Arrow | Zero-copy, cross-language |
| Game/mobile | FlatBuffers | Zero-copy, instant access |
| MongoDB | BSON | Native format |
| Logging | JSON / MessagePack | Flexible, searchable |
| ML model serving | Protobuf / Arrow | Fast, typed |

---

## EVOLUTION AND TRENDS

### Timeline

```mermaid
timeline
    title Serialization Format Evolution
    section Text Era
        2001 : XML - verbose, text-based
        2006 : JSON - simpler, universal
    section Binary Era
        2008 : Protocol Buffers - binary, schema
        2009 : Apache Avro - schema evolution
        2011 : MessagePack - binary JSON
    section Columnar Era
        2013 : Apache Parquet - columnar storage
        2013 : Apache ORC - Hive optimized
        2014 : FlatBuffers - zero-copy
    section In-Memory Era
        2016 : Apache Arrow - in-memory columnar
        2020 : Arrow Flight - high-perf transport
```

### Current Trends

```mermaid
graph TD
    subgraph Trends[" "]
        Trends_title["Current Trends (2025+)"]
        style Trends_title fill:none,stroke:none,color:#333,font-weight:bold
        T1["Columnar Everywhere<br/>Parquet for storage<br/>Arrow for compute"]
        T2["Schema Registries<br/>Confluent, AWS Glue<br/>Centralized schema management"]
        T3["Zero-Copy / Memory-Mapped<br/>Arrow Flight for transport<br/>FlatBuffers for access"]
        T4["Arrow as Lingua Franca<br/>Cross-system data exchange<br/>Python↔Rust↔Java↔Go"]
        T5["Format Convergence<br/>Parquet + Arrow + Flight<br/>= Complete data platform"]
    end

    style Trends fill:#e8f5e9
```

---

## REFERENCES

### Specifications
1. Apache Avro: https://avro.apache.org/docs/current/specification/
2. Protocol Buffers: https://protobuf.dev/programming-guides/encoding/
3. Apache Parquet: https://github.com/apache/parquet-format
4. Apache ORC: https://orc.apache.org/specification/
5. Apache Arrow: https://arrow.apache.org/docs/format/Columnar.html
6. FlatBuffers: https://google.github.io/flatbuffers/flatbuffers_internals.html

### Papers
- Melnik, S. et al. "Dremel: Interactive Analysis of Web-Scale Datasets." VLDB, 2010.
- McKinney, W. "Apache Arrow and the Future of Data Frames." 2020.

### Tools & Libraries
- Apache Arrow: https://github.com/apache/arrow
- Apache Parquet: https://github.com/apache/parquet-java
- Confluent Schema Registry: https://github.com/confluentinc/schema-registry
- Buf (Protobuf): https://github.com/bufbuild/buf
- Apache Avro: https://github.com/apache/avro

---

*Document Version: 2.0*
*Last Updated: February 2026*
