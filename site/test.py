from extraction.model.extractmodel import ExtractionModel

def main():
    model = ExtractionModel("movie")
#    model.extract("Ryan Gosling in the movie Drive where the driver finds himself entagled in a crime syndicate")
    dt = model.extract('Blade Runner is a 1982 science fiction film directed by Ridley Scott This film is set in a dystopian future Lost Angeles of 2019') 
    print(dt)
#    model.extract("i m thinking of a 1988 action film in which bruce willis a nypd officer fights off terrorists")
#in which synthetic humans known as replicants are bio-engineered by the powerful Tyrell Corporation to work on off-world Colonies. Written by hampton Francher and David Peoples')

main()
