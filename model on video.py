from ultralytics import YOLO

modelPath= 'PATH_TO_MODEL'
model = YOLO(r'D:\floodYolo\runs\detect\train\weights\best.pt')


path= 'PATH_TO_FILE'
source = r'C:\Users\whudd\Downloads\test.mp4'

# Run inference on the source

results = model.predict(source, show=True, save=True,device=0)  # generator of Results objects
