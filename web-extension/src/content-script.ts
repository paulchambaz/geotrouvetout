function createLocateButton(): HTMLElement {
  const locateButton = document.createElement('button');
  locateButton.textContent = 'LOCATE';
  locateButton.style.padding = '5px 20px';
  locateButton.style.fontSize = 'var(--font-size-12)';
  locateButton.style.color = 'white';
  locateButton.style.backgroundColor = 'var(--ds-color-green-80)';
  locateButton.style.border = 'none';
  locateButton.style.borderRadius = '20px';
  locateButton.style.display = 'inline-block';
  locateButton.style.cursor = 'pointer';
  locateButton.style.fontFamily = 'var(--default-font), sans-serif';
  locateButton.style.fontWeight = '700';
  locateButton.style.fontStyle = 'italic';
  locateButton.style.marginLeft = '32px';

  locateButton.addEventListener('mouseenter', () => {
    locateButton.style.transform = 'scale(1.1)';
    locateButton.style.transition = 'transform 0.1s ease-out';
  });

  locateButton.addEventListener('mouseleave', () => {
    locateButton.style.transform = 'scale(1)';
    locateButton.style.transition = 'transform 0.1s ease-out';
  });


  const ticketBarMeta = document.querySelector('[class^="ticket-bar_meta"]');
  ticketBarMeta.appendChild(locateButton);

  return locateButton;
}

function captureVisibleImage() {
  const canvas = document.querySelector('canvas.mapsConsumerUiSceneInternalCoreScene__canvas.widget-scene-canvas') as HTMLCanvasElement;
  if (canvas) {
    const image = document.createElement('img');
    image.crossOrigin = 'anonymous';
    image.src = canvas.toDataURL('image/png');

    const imageDataUrl = (image as HTMLImageElement).src;
    return imageDataUrl;
  } else {
    throw new Error('Unable to find the canvas element');
  }
}

async function processImage(imageDataUrl: string): Promise<HTMLCanvasElement[]> {
  const image = new Image();
  image.src = imageDataUrl;
  await new Promise((resolve) => (image.onload = resolve));

  const width = image.width;
  const height = image.height;

  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = width;
  canvas.height = height;
  context.drawImage(image, 0, 0);

  const squareSize = height;
  const fullSquares = Math.floor(width / squareSize);
  const finalSquarePosition = width - squareSize;

  const resizedSubImages: HTMLCanvasElement[] = [];

  for (let i = 0; i <= fullSquares; i++) {
    const offsetX = i < fullSquares ? i * squareSize : finalSquarePosition;

    const subImageCanvas = document.createElement('canvas');
    const subImageContext = subImageCanvas.getContext('2d');
    subImageCanvas.width = 640;
    subImageCanvas.height = 640;

    subImageContext.drawImage(canvas, offsetX, 0, squareSize, squareSize, 0, 0, 640, 640);

    resizedSubImages.push(subImageCanvas);
  }

  return resizedSubImages;
}

async function sendImageToAPI(canvas: HTMLCanvasElement): Promise<Response> {
  console.log('a');
  const context = canvas.getContext('2d');
  console.log('b');
  const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
  console.log('c');
  const { data, width, height } = imageData;

  console.log('d');
  const byteArray = new Uint8Array(data.length);

  console.log('e');
  for (let i = 0; i < data.length; i++) {
    byteArray[i] = data[i];
  }

  console.log('f');
  const blob = new Blob([byteArray], { type: 'image/png' });
  console.log('g');
  const formData = new FormData();
  formData.append('file', blob, 'image.png');

  console.log('h');
  const response = await fetch('https://geotrouvetout.chambaz.xyz/locate', {
    method: 'POST',
    body: formData,
  });

  return response;
}

const locateButton = createLocateButton();
locateButton.addEventListener('click', async () => {
  try {
    // get the image from the canvas
    console.log('pressing button');
    const visibleImageDataUrl = captureVisibleImage();
    console.log('got canvas image');
    console.log(visibleImageDataUrl);

    // cut the image into subimages
    const imageUrls = await processImage(visibleImageDataUrl);
    console.log('got sub images');

    for (let i = 0; i < imageUrls.length; i++) {
      console.log(imageUrls[i]);
    }

    // do the geotrouvetout rest api request
    const apiResponses = await Promise.all(imageUrls.map(sendImageToAPI));

    // combine the resulting dictionaries to get quality information

    } catch (error) {
    console.error('Error capturing visible image : ', error);
  }
});
