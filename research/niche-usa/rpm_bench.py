# Public US RPM planning benchmarks (OutlierKit niche table, 2026; ranges are third-party estimates, not measurements).
# Each topic -> (benchmark group, low, high). Groups without an OutlierKit row are mapped to the closest row and marked '~'.
G = {
 'Personal Finance': (10, 25), 'Legal & Tax': (8, 22), 'Business & SaaS': (8, 19), 'Real Estate': (7, 17),
 'Software Reviews': (6, 14), 'Career & Jobs': (5, 12), 'Health (Science)': (4, 11), 'AI & Technology': (4, 11),
 'Motivation': (3, 8), 'True Crime': (3, 7), 'History': (3, 7), 'Relaxation': (2, 6), 'Food & Recipe': (2, 6),
 'Travel': (2, 5), 'Sports': (2, 4), 'Entertainment': (1, 3), '~DIY/Home (≈Health)': (4, 11), '~Outdoors/Hobby (≈Food)': (2, 6),
 '~Science/Education (≈Health)': (4, 11), '~Religion/Philosophy (≈Motivation)': (3, 8), '~Parenting/Relationships': (4, 10),
}
T = {
 'personal finance budgeting': 'Personal Finance', 'retirement planning social security medicare': 'Personal Finance',
 'stock market investing dividends': 'Personal Finance', 'credit score credit cards debt': 'Personal Finance',
 'frugal living saving money': 'Personal Finance', 'insurance explained': 'Personal Finance',
 'taxes IRS tax tips': 'Legal & Tax', 'estate planning wills trusts probate': 'Legal & Tax', 'legal rights know your rights': 'Legal & Tax',
 'lawyer reacts legal analysis': 'Legal & Tax', 'disability benefits SSDI': 'Legal & Tax', 'veterans VA benefits': 'Legal & Tax',
 'small business owner advice': 'Business & SaaS', 'side hustles make money online': 'Business & SaaS', 'economics explained': 'Business & SaaS',
 'business documentaries company stories': 'Business & SaaS', 'corporate fraud white collar crime documentary': 'True Crime',
 'real estate investing landlord': 'Real Estate', 'housing market mortgage rates': 'Real Estate', 'home buying first time buyer': 'Real Estate',
 'luxury real estate home tours': 'Real Estate', 'tiny homes': 'Real Estate',
 'Excel and software tutorials': 'Software Reviews', 'AI tools tutorials': 'AI & Technology', 'cybersecurity explained': 'AI & Technology',
 'electric vehicles EV news': 'AI & Technology', 'car buying advice dealership': 'Personal Finance',
 'trade jobs electrician plumber careers': 'Career & Jobs', 'trucking industry truck drivers': 'Career & Jobs', 'airline pilots aviation': 'Career & Jobs',
 'senior health tips for older adults': 'Health (Science)', 'doctor explains medical education': 'Health (Science)',
 'nutrition longevity healthy aging': 'Health (Science)', 'fitness over 50': 'Health (Science)', 'weight loss diet': 'Health (Science)',
 'mental health anxiety therapy': 'Health (Science)', "menopause women's health": 'Health (Science)', "men's health testosterone": 'Health (Science)',
 'sleep science insomnia': 'Health (Science)', 'elder care caregiving dementia': 'Health (Science)', 'psychology human behavior': 'Motivation',
 'stoicism philosophy': 'Motivation', 'relationship advice marriage': '~Parenting/Relationships', 'Bible study Christian teaching': '~Religion/Philosophy (≈Motivation)',
 'true crime documentary': 'True Crime', 'courtroom trials court cases': 'True Crime', 'police bodycam footage': 'True Crime',
 'prison life documentary': 'True Crime', 'cold cases unsolved murders': 'True Crime', 'interrogation analysis': 'True Crime',
 'missing persons cases': 'True Crime', 'mafia organized crime history': 'True Crime', 'scams fraud con artists stories': 'True Crime',
 'famous heists robbery documentary': 'True Crime', 'unsolved mysteries': 'True Crime', 'conspiracy theories explained': 'Entertainment',
 'HOA horror stories neighbor disputes': 'Entertainment', 'reddit stories narration revenge': 'Entertainment',
 'World War 2 history documentary': 'History', 'military history battles': 'History', 'ancient history civilizations': 'History',
 'American history presidents': 'History', 'Cold War history': 'History', 'history documentary for sleep': 'Relaxation',
 'aviation disasters plane crash investigation': 'History', 'shipwrecks maritime disasters': 'History', 'engineering failures disasters': 'History',
 'archaeology discoveries': 'History', 'old Hollywood classic movie stars': 'Entertainment', 'classic TV shows nostalgia': 'Entertainment',
 'rock music history': 'Entertainment', 'celebrity documentaries': 'Entertainment', 'movie explained film analysis': 'Entertainment',
 'boxing history': 'Sports', 'pro wrestling history': 'Sports', 'NFL football analysis': 'Sports', 'golf instruction': 'Sports', 'chess': 'Sports',
 'home improvement DIY repairs': '~DIY/Home (≈Health)', 'woodworking': '~DIY/Home (≈Health)', 'homesteading off grid': '~DIY/Home (≈Health)',
 'gardening vegetable garden': '~DIY/Home (≈Health)', 'tools reviews': 'Software Reviews', 'auto repair mechanic': '~DIY/Home (≈Health)',
 'classic car restoration': '~DIY/Home (≈Health)', 'RV living full time': 'Travel', 'national parks USA travel': 'Travel',
 'bass fishing': '~Outdoors/Hobby (≈Food)', 'hunting deer elk': '~Outdoors/Hobby (≈Food)', 'firearms gun reviews': '~Outdoors/Hobby (≈Food)',
 'survival prepping': '~Outdoors/Hobby (≈Food)', 'BBQ smoking meat cooking': 'Food & Recipe', 'wildlife nature documentary': '~Science/Education (≈Health)',
 'space astronomy universe': '~Science/Education (≈Health)', 'audiobooks classic literature': 'Relaxation', 'life stories of elderly people': 'Entertainment',
 'paranormal ghost stories': 'Entertainment', 'horror stories narration': 'Entertainment', 'geopolitics analysis': 'Entertainment',
 'US politics commentary': 'Entertainment',
}
def bench(topic):
    g = T.get(topic)
    if not g: return None, None, None
    lo, hi = G[g]; return g, lo, hi
