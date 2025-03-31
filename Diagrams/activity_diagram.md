```mermaidp
flowchart TD
    A[Start Bot] --> B[Initialize Models]
    B --> C[Configure Logging]
    C --> D{Waiting for User Interaction}

    D --> |/start Command| E[Generate Welcome Message]
    E --> |Send Message| F{Validate Command}
    F --> D
    
    D --> |/help Command| G[Display Help Instructions]
    G --> |Send Detailed Instructions| H{Validate Command}
    H --> D

    D --> |User Sends Message| I[Preprocess Message Text]

    I --> J[Extract URLs from Message]
    J --> K{URLs Detected?}
    K --> |Yes| L[Preprocess Each URL]
    L --> M[Apply Link Vectorizer]
    M --> N[Predict Malicious Link]
    N --> |Malicious Link Found| O[Generate Malicious Link Warning]
    O --> P[Log Malicious Link Detection]
    P --> D
    K --> |No| Q[Skip URL Detection]

    Q --> R[Clean Text]
    R --> S[Vectorize Message]
    S --> T[Apply Spam Detection Model]
    T --> |Spam Detected| U[Generate Spam Warning]
    U --> V[Log Spam Detection]
    V --> D
    T --> |Not Spam| W[Continue Analysis]

    W --> X[Extract News Components]
    X --> Y{Sufficient Text Length?}
    Y --> |Yes| Z[Prepare Title and Content]
    Z --> AA[Apply Combined News Model]
    AA --> |Fake News Detected| AB[Generate Fake News Warning]
    AB --> AC[Include Detection Confidence]
    AC --> AD[Log Fake News Detection]
    AD --> D

    D --> |/checknews Command| AE{Command Source}
    AE --> |Direct Text| AF[Process Provided Text]
    AE --> |Replied Message| AG[Extract Replied Message Text]
    AF --> AH[Perform Detailed News Analysis]
    AG --> AH
    AH --> AI[Generate Comprehensive News Report]
    AI --> D

    D --> |Error Occurs| AJ[Capture Error Details]
    AJ --> AK[Log Error]
    AK --> AL[Send Error Message to User]
    AL --> D
    
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style D fill:#bbf,stroke:#333,stroke-width:3px
    style I fill:#bfb,stroke:#333,stroke-width:2px
    style W fill:#ffa500,stroke:#333,stroke-width:2px
    style AE fill:#00CED1,stroke:#333,stroke-width:2px
    style AJ fill:#FF6347,stroke:#333,stroke-width:2px
```