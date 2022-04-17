network_info = {
    'mainnet': {
        'url': 'https://lcd.terra.dev',
        'moniker': 'columbus-5'
    },
    'testnet': {
        'url': 'https://bombay-lcd.terra.dev',
        'moniker': 'bombay-12'
    }
}

gas = {
    "gas_prices": "0.15uusd",
    "gas_adjustment": "1.4"
}

nebula_contracts = {  # TODO: update contract addresses when deployed
    "mainnet": {
        "nebula_airdrop": "NEBULA_AIRDROP",
        "nebula_cluster_factory": "NEBULA_CLUSTER_FACTORY",
        "nebula_collector": "NEBULA_COLLECTOR",
        "nebula_community": "NEBULA_COMMUNITY",
        "nebula_gov": "NEBULA_GOV",
        "nebula_incentives_custody": "NEBULA_INCENTIVES_CUSTODY",
        "nebula_incentives": "NEBULA_INCENTIVES",
        "nebula_lp_staking": "NEBULA_LP_STAKING",
        "nebula_oracle": "NEBULA_ORACLE",
        "nebula_token": "NEBULA_TOKEN"
    },
    "testnet": {
        "nebula_airdrop": "NEBULA_AIRDROP",
        "nebula_cluster_factory": "terra103srr94gy8zgyey7ncg63gqfgac3y6nkdc28jh",
        "nebula_collector": "terra1xk7a2yhm2a7ylkns73e0vg50lv6l7cv0n02rhq",
        "nebula_community": "terra1acmfgylk8chxw7lxwmkzv3gzdesk4vfjpng0d5",
        "nebula_gov": "terra13psqttx8wzmedtmd7g4mhtyqdvujnryzgwuy84",
        "nebula_incentives_custody": "terra1cn985mqxtk9hxlc67a5nh52pkx2vcvtt2jzwdz",
        "nebula_incentives": "terra19lrxyn8ps7w733y69a05ulkseg4dlh649yag86",
        "nebula_lp_staking": "terra1tzjhck0r8c0np7yazhj9jr5cmn53uut6u7rh67",
        "nebula_oracle": "terra1uyts5f7lpe4xpwwqgc42yemxk5ndvqrgsx9zd3",
        "nebula_token": "terra1hwts6pfqyj8c833m6f9djzwtlhzvdc9yx2ve5e"
    }
}

cluster_contracts = {
    "mainnet": {
        "terraform": ""
    },
    "testnet": {
        # "terraform": "terra1ae33wpqqymjyrgjc4fexzz4msl7qwclmvxzrvy"
        'tottenham': 'terra1247eqmv9y7rc8k98jl4ps7c0kmmt4hm6uvfawq',
        'lunaust': 'terra1f08qvrr4gpwdxqlxpgg559kdc5wl2gzgh3c00a',
        'all_star_assets': 'terra1hxus0egh2j6y9j3qm2hhu6d2fzeugnv073hnev',
        'first_three_cluster': 'terra1r3vkk9vcajvjt8g9895jf84pyp6hcmwfq2vg9f',
        'mirancust': 'terra1rhuwcluvgnql4f0xlhzmxlrgk22q65ym646sk2',
        'tester': 'terra1x40z523saslsuwaqysf59tudcrhprzp9g6esus',
    }
}

market_contracts = {
    'testnet': {
        'astroport_factory': "terra15jsahkaf9p0qu8ye873p0u5z6g07wdad0tdq43"
        },
    'mainnet': {

    }
}