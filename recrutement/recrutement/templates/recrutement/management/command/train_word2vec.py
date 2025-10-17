# recrutement/management/commands/train_word2vec.py
from django.core.management.base import BaseCommand
from recrutement.models import OffreEmploi, Candidat
from recrutement.nlp_matching import build_corpus_from_offres_and_candidats, train_model

class Command(BaseCommand):
    help = "Entraîne / reconstruit le modèle Word2Vec à partir des offres et candidats."

    def add_arguments(self, parser):
        parser.add_argument('--rebuild', action='store_true', help='Forcer la reconstruction du modèle')

    def handle(self, *args, **options):
        rebuild = options['rebuild']
        offres = OffreEmploi.objects.all()
        candidats = Candidat.objects.all()
        corpus = build_corpus_from_offres_and_candidats(offres, candidats)
        if not corpus:
            self.stdout.write(self.style.ERROR("Corpus vide : vérifie que tu as des offres / candidats."))
            return
        model = train_model(corpus, rebuild=rebuild)
        self.stdout.write(self.style.SUCCESS("Modèle entraîné et sauvegardé."))
