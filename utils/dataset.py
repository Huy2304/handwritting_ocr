from torchvision import datasets, transforms

def get_datasets(train_dir, val_dir):
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_ds = datasets.ImageFolder(train_dir, transform)
    val_ds   = datasets.ImageFolder(val_dir, transform)

    return train_ds, val_ds
