import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight # New import
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt

# --- 1. Data Preparation (Unchanged) ---
base_dir = 'dataset'
image_dir = os.path.join(base_dir, 'all_images')
metadata_path = os.path.join(base_dir, 'HAM10000_metadata.csv')
df = pd.read_csv(metadata_path)
image_path_dict = {os.path.splitext(fname)[0]: os.path.join(image_dir, fname) for fname in os.listdir(image_dir)}
df['path'] = df['image_id'].map(image_path_dict.get)
lesion_type_dict = { 'nv': 'Melanocytic Nevi', 'mel': 'Melanoma', 'bkl': 'Benign Keratosis-like Lesions', 'bcc': 'Basal Cell Carcinoma', 'akiec': 'Actinic Keratoses', 'vasc': 'Vascular Lesions', 'df': 'Dermatofibroma' }
df['cell_type'] = df['dx'].map(lesion_type_dict.get)

# --- 2. Splitting the Data (Unchanged) ---
X = df['path']
y = df['cell_type']
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
train_df = pd.DataFrame({'path': X_train, 'cell_type': y_train})
val_df = pd.DataFrame({'path': X_val, 'cell_type': y_val})

# --- 3. Image Data Augmentation (Unchanged) ---
IMG_SIZE = 224
train_datagen = ImageDataGenerator(
    rescale=1./255, rotation_range=20, width_shift_range=0.1,
    height_shift_range=0.1, shear_range=0.1, zoom_range=0.1,
    horizontal_flip=True, fill_mode='nearest'
)
val_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_dataframe(
    train_df, x_col='path', y_col='cell_type', target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32, class_mode='categorical'
)
validation_generator = val_datagen.flow_from_dataframe(
    val_df, x_col='path', y_col='cell_type', target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32, class_mode='categorical', shuffle=False
)

# --- 4. Building the Model (Unchanged) ---
base_model = MobileNetV2(input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights='imagenet')
base_model.trainable = False
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(len(train_generator.class_indices), activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)

# --- 5. Compiling and Training the Model (MODIFIED) ---
model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

# --- NEW: Calculate Class Weights ---
# This tells the model to pay more attention to the classes with fewer images.
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)
class_weight_dict = dict(enumerate(class_weights))

print("--- Class Weights ---")
print(class_weight_dict)
print("---------------------")

# --- MODIFIED: Train the model with the class weights ---
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size,
    epochs=15, # Increased epochs for better learning
    class_weight=class_weight_dict # Apply the weights here
)

# --- 6. Saving and Plotting (Unchanged) ---
print("Saving the newly trained balanced model...")
model.save('skin_cancer_model_trained.h5')
print("Model saved as skin_cancer_model_trained.h5")

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy'); plt.legend()
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss'); plt.legend()
plt.savefig('training_history.png')
plt.show()