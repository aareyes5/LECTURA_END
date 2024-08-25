import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Leer los datos del archivo Excel
data = pd.read_excel('datos.xlsx')

# Convertir la columna "Sexo" a valores numéricos (0 para Femenino, 1 para Masculino)
data['Sexo'] = data['Sexo'].map({'F': 0, 'M': 1})

# Seleccionar las características (inputs) Edad, Sexo y Preguntas 2-10
X = data[['Edad', 'Sexo', 'Pregunta2', 'Pregunta3', 'Pregunta4', 'Pregunta5', 'Pregunta6', 'Pregunta7', 'Pregunta8', 'Pregunta9', 'Pregunta10']]
# Seleccionar las etiquetas (outputs) Preguntas 2-10
y = data[['Pregunta2', 'Pregunta3', 'Pregunta4', 'Pregunta5', 'Pregunta6', 'Pregunta7', 'Pregunta8', 'Pregunta9', 'Pregunta10']]

# Dividir los datos en conjunto de entrenamiento y de prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Estandarizar los datos
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Guardar el scaler para usarlo más tarde
joblib.dump(scaler, 'scaler.pkl')

# Crear el modelo de la red neuronal
model = Sequential()
model.add(Dense(128, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(y_train.shape[1]))  # 9 nodos de salida, uno para cada pregunta

# Compilar el modelo
model.compile(optimizer='adam', loss='mean_squared_error')

# Entrenar el modelo
model.fit(X_train, y_train, epochs=100, batch_size=10, validation_split=0.2)

# Evaluar el modelo
loss = model.evaluate(X_test, y_test)
print(f'Pérdida del modelo: {loss}')

# Guardar el modelo
model.save('madrs_model.h5')
