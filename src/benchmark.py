from os.path import join
from pathlib import Path
from time import time
from sklearn.metrics import f1_score, accuracy_score
from BenchmarkTable import BenchmarkTable
from pdf_features.PdfFeatures import PdfFeatures
from pdf_token_type_labels.load_labeled_data import load_labeled_data
from pdf_tokens_type_trainer.ModelConfiguration import ModelConfiguration
from pdf_tokens_type_trainer.TokenTypeTrainer import TokenTypeTrainer
from pdf_tokens_type_trainer.config import PDF_LABELED_DATA_ROOT_PATH

BENCHMARK_MODEL = join(Path(__file__).parent.parent, "model", "benchmark.model")
model_configuration = ModelConfiguration()


def train_for_benchmark():
    Path(BENCHMARK_MODEL).parent.mkdir(exist_ok=True)
    all_train_pdf_features = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="train")
    trainer = TokenTypeTrainer(all_train_pdf_features, model_configuration)
    labels = [token.token_type.get_index() for token in trainer.loop_tokens()]
    trainer.train(BENCHMARK_MODEL, labels)


def predict_for_benchmark(pdfs_features: list[PdfFeatures]):
    print("Prediction PDF number", len(pdfs_features))
    trainer = TokenTypeTrainer(pdfs_features, model_configuration)
    truths = [token.token_type.get_index() for token in trainer.loop_tokens()]

    print("predicting")
    trainer.predict(BENCHMARK_MODEL)
    predictions = [token.prediction for token in trainer.loop_tokens()]
    return truths, predictions


def benchmark(get_granular_scores: bool):
    train_for_benchmark()
    test_pdf_features = load_labeled_data(PDF_LABELED_DATA_ROOT_PATH, filter_in="test")
    start_time = time()
    truths, predictions = predict_for_benchmark(test_pdf_features)
    total_time = time() - start_time
    if get_granular_scores:
        benchmark_table = BenchmarkTable(test_pdf_features, total_time)
        benchmark_table.prepare_benchmark_table()

    f1 = round(f1_score(truths, predictions, average="macro") * 100, 2)
    accuracy = round(accuracy_score(truths, predictions) * 100, 2)
    print(f"F1 score {f1}%")
    print(f"Accuracy score {accuracy}%")


if __name__ == "__main__":
    print("start")
    start = time()
    benchmark(True)
    print("finished in", time() - start, "seconds")
